"""
Photo upload workflow: pre-signed URLs → direct-to-S3 PUT → completion callback → Celery processing.
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.storage import StorageManager, get_storage_manager
from app.db.session import get_db
from app.models.event import Event
from app.models.face import Upload
from app.models.photo import Photo
from app.models.user import User
from app.schemas.photo import PresignedUrlRequest, PresignedUrlResponse, UploadInitiateResponse
from app.services.isolation import check_event_access
from app.services.pipeline import process_photos_batch

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/{event_id}/upload-initiate", response_model=UploadInitiateResponse)
def initiate_batch_upload(
    event_id: str,
    req_in: PresignedUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageManager = Depends(get_storage_manager),
):
    """
    Step 1: Generate pre-signed PUT URLs so the client can upload directly to S3/MinIO.
    """
    check_event_access(db, current_user, event_id)

    # Validate file extensions
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
    from pathlib import Path
    for filename in req_in.filenames:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' is not allowed. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

    upload_id = str(uuid.uuid4())

    upload = Upload(
        upload_id=upload_id,
        event_id=event_id,
        photographer_id=current_user.user_id,
        total_files=len(req_in.filenames),
        status="pending",
    )
    db.add(upload)

    urls: List[PresignedUrlResponse] = []
    for filename in req_in.filenames:
        safe_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        obj_key = StorageManager.build_object_key(event_id, str(current_user.user_id), safe_name)
        put_url = storage.generate_presigned_upload_url(obj_key)

        db.add(Photo(
            event_id=event_id,
            photographer_id=current_user.user_id,
            image_path=obj_key,
            upload_id=upload_id,
        ))
        urls.append(PresignedUrlResponse(filename=filename, upload_url=put_url, object_key=obj_key))

    db.commit()
    return UploadInitiateResponse(upload_id=upload_id, urls=urls)


@router.post("/{event_id}/upload-complete/{upload_id}")
def complete_batch_upload(
    event_id: str,
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Step 2: Client signals files are uploaded → enqueue Celery processing job.
    """
    check_event_access(db, current_user, event_id)

    upload = db.query(Upload).filter(Upload.upload_id == upload_id, Upload.event_id == event_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload batch not found")
    if upload.status != "pending":
        return {"status": "already_started", "current_status": upload.status}

    photo_ids = [
        p.photo_id
        for p in db.query(Photo).filter(Photo.upload_id == upload_id, Photo.event_id == event_id).all()
    ]
    if not photo_ids:
        raise HTTPException(status_code=400, detail="No photos found in this batch")

    process_photos_batch.delay(upload_id, event_id, photo_ids)
    return {"status": "queued", "photo_count": len(photo_ids)}


@router.get("/{event_id}/upload-status/{upload_id}")
def get_upload_status(
    event_id: str,
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_event_access(db, current_user, event_id)
    upload = db.query(Upload).filter(Upload.upload_id == upload_id, Upload.event_id == event_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload batch not found")

    return {
        "upload_id": upload.upload_id,
        "status": upload.status,
        "total_files": upload.total_files,
        "processed_files": upload.processed_files,
        "faces_extracted": upload.faces_extracted,
        "created_at": upload.created_at,
    }


@router.get("/{event_id}/gallery")
def get_event_gallery(
    event_id: str,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageManager = Depends(get_storage_manager),
):
    """Paginated photo gallery for an event."""
    check_event_access(db, current_user, event_id)

    total = db.query(Photo).filter(Photo.event_id == event_id).count()
    offset = (page - 1) * limit

    photos = (
        db.query(Photo)
        .filter(Photo.event_id == event_id)
        .order_by(Photo.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "photos": [
            {
                "photo_id": p.photo_id,
                "image_path": p.image_path,
                "download_url": storage.generate_presigned_download_url(p.image_path),
                "created_at": str(p.created_at) if p.created_at else None,
            }
            for p in photos
        ],
    }


@router.get("/{event_id}/uploads")
def list_event_uploads(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all upload batches for a specific event."""
    from app.api.routes.photos import check_event_access
    check_event_access(db, current_user, event_id)
    
    uploads = (
        db.query(Upload)
        .filter(Upload.event_id == event_id)
        .order_by(Upload.created_at.desc())
        .all()
    )
    
    return [
        {
            "upload_id": u.upload_id,
            "status": u.status,
            "total_files": u.total_files,
            "processed_files": u.processed_files,
            "faces_extracted": u.faces_extracted,
            "created_at": str(u.created_at) if u.created_at else None,
        }
        for u in uploads
    ]
