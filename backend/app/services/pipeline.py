"""
Celery application + background task for the face-detection / embedding pipeline.

Steps per photo:
  1. Download original from object storage
  2. Decode with OpenCV
  3. RetinaFace detection → bounding boxes + 5-point landmarks
  4. Affine alignment via eye landmarks
  5. Quality gate: blur (Laplacian variance) + minimum face size
  6. ArcFace → 512-D unit-normalised embedding
  7. Persist Face rows (with pgvector embedding) to PostgreSQL
  8. After batch completes → trigger clustering
"""
import logging
from typing import List, Tuple

import cv2
import insightface
import numpy as np
from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.storage import get_storage_manager
from app.db.session import SessionLocal
# Import all models via db.base so SQLAlchemy resolves all relationships
# (Face has relationship("Event"), so Event must be registered first)
from app.db.base import Face, Upload, Photo

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Celery app (single instance, shared with clustering.py) ─────────────
celery_app = Celery(
    "eventsnap",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# ── Lazy-loaded InsightFace model ────────────────────────────────────────
_face_app: insightface.app.FaceAnalysis | None = None


def _get_face_app() -> insightface.app.FaceAnalysis:
    global _face_app
    if _face_app is None:
        _face_app = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
        logger.info("InsightFace buffalo_l model loaded successfully")
    return _face_app


# ── Image helpers ────────────────────────────────────────────────────────

def _estimate_blur(face_img: np.ndarray) -> float:
    """Laplacian variance — higher is sharper."""
    if face_img is None or face_img.size == 0:
        return 0.0
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _align_face(img: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
    """Rotate image so the two eyes are horizontal."""
    if landmarks is None or len(landmarks) < 2:
        return img
    left_eye, right_eye = landmarks[0], landmarks[1]
    angle = float(np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0])))
    center = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    h, w = img.shape[:2]
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC)


# ── Core extraction function ────────────────────────────────────────────

def extract_and_assess_faces(
    image_bytes: bytes,
) -> List[Tuple[List[int], float, List[float]]]:
    """
    Returns list of ``(bbox_xywh, quality_score, embedding_512)`` tuples.
    Raises ValueError if the image cannot be decoded.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes")

    app = _get_face_app()
    faces = app.get(img)
    results: List[Tuple[List[int], float, List[float]]] = []

    min_px = settings.FACE_MIN_SIZE_PX
    blur_thr = settings.FACE_BLUR_THRESHOLD

    for face in faces:
        bbox = face.bbox.astype(int).tolist()  # [x1, y1, x2, y2]
        w_box, h_box = bbox[2] - bbox[0], bbox[3] - bbox[1]

        if w_box < min_px or h_box < min_px:
            continue

        aligned = _align_face(img, face.kps)
        x1 = max(0, bbox[0])
        y1 = max(0, bbox[1])
        x2 = min(img.shape[1], bbox[2])
        y2 = min(img.shape[0], bbox[3])
        crop = aligned[y1:y2, x1:x2]

        blur = _estimate_blur(crop)
        if blur < blur_thr:
            continue

        quality = min(100.0, blur / 5.0 + w_box / 10.0)
        emb = face.embedding / np.linalg.norm(face.embedding)

        results.append(([bbox[0], bbox[1], w_box, h_box], quality, emb.tolist()))

    return results


# ── Celery task ──────────────────────────────────────────────────────────

@celery_app.task(name="tasks.process_photos_batch", bind=True, max_retries=2)
def process_photos_batch(self, upload_id: str, event_id: str, photo_ids: List[int]) -> dict:
    """Process a batch of photos: detect → align → embed → persist."""
    db: Session = SessionLocal()
    processed = 0
    total_faces = 0
    storage = get_storage_manager()

    try:
        upload = db.query(Upload).filter(Upload.upload_id == upload_id).first()
        if not upload:
            return {"status": "error", "message": f"Upload {upload_id} not found"}

        upload.status = "processing"
        upload.total_files = len(photo_ids)
        db.commit()

        photos = db.query(Photo).filter(
            Photo.photo_id.in_(photo_ids),
            Photo.event_id == event_id,
        ).all()

        for photo in photos:
            try:
                img_bytes = storage.download_file_bytes(photo.image_path)
                faces_data = extract_and_assess_faces(img_bytes)

                for bbox, quality, embedding in faces_data:
                    db.add(Face(
                        event_id=event_id,
                        photo_id=photo.photo_id,
                        bbox=bbox,
                        quality_score=quality,
                        embedding=embedding,
                    ))
                    total_faces += 1

                processed += 1
                upload.processed_files = processed
                upload.faces_extracted = total_faces
                db.commit()
            except Exception:
                logger.exception("Failed processing photo %s", photo.photo_id)

        upload.status = "completed"
        db.commit()

        # Trigger person clustering
        from app.services.clustering import trigger_clustering_for_event
        trigger_clustering_for_event(event_id)

    except Exception as exc:
        db.rollback()
        try:
            upload.status = "failed"
            db.commit()
        except Exception:
            pass
        logger.exception("Batch %s failed", upload_id)
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()

    return {"status": "success", "processed": processed, "faces": total_faces}
