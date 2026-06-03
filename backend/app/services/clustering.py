"""
HDBSCAN / DBSCAN face clustering within a single event.

Called automatically after a batch upload finishes.
Reads all face embeddings for event_id, clusters them, and writes Person + PersonPhoto rows.
"""
import logging
from typing import List

import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.face import Face, Person, PersonPhoto
from app.services.pipeline import celery_app          # single Celery instance

logger = logging.getLogger(__name__)


def _try_hdbscan(X: np.ndarray):
    """Attempt HDBSCAN (available in scikit-learn ≥ 1.3). Returns labels or None."""
    try:
        from sklearn.cluster import HDBSCAN
        clusterer = HDBSCAN(min_cluster_size=2, metric="euclidean")
        clusterer.fit(X)
        logger.info("HDBSCAN succeeded")
        return clusterer.labels_
    except Exception as exc:
        logger.warning("HDBSCAN unavailable or failed (%s), falling back to DBSCAN", exc)
        return None


def run_clustering_for_event(db: Session, event_id: str) -> int:
    """
    Cluster all face embeddings for *event_id* and rebuild Person mappings.
    Returns the number of distinct persons created.
    """
    faces: List[Face] = db.query(Face).filter(Face.event_id == event_id).all()
    if len(faces) < 2:
        logger.info("Event %s: %d faces — skipping clustering", event_id, len(faces))
        return 0

    embeddings, face_ids, photo_ids = [], [], []
    for f in faces:
        emb = np.array(f.embedding, dtype=np.float32)
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb /= norm
        embeddings.append(emb)
        face_ids.append(f.face_id)
        photo_ids.append(f.photo_id)

    X = np.vstack(embeddings)

    # Try HDBSCAN first, fall back to DBSCAN
    labels = _try_hdbscan(X)
    if labels is None:
        clusterer = DBSCAN(eps=0.45, min_samples=2, metric="cosine")
        clusterer.fit(X)
        labels = clusterer.labels_
        logger.info("DBSCAN succeeded for event %s", event_id)

    # Clear existing person data for this event
    existing = db.query(Person).filter(Person.event_id == event_id).all()
    existing_ids = [p.person_id for p in existing]
    if existing_ids:
        db.query(PersonPhoto).filter(PersonPhoto.person_id.in_(existing_ids)).delete(synchronize_session=False)
        db.query(Person).filter(Person.event_id == event_id).delete(synchronize_session=False)
    db.flush()

    # Write new clusters
    person_count = 0
    for label in set(labels):
        if label == -1:
            continue
        person_count += 1
        person = Person(event_id=event_id, name=f"Person_{person_count:03d}")
        db.add(person)
        db.flush()

        for idx in np.where(labels == label)[0]:
            db.add(PersonPhoto(
                person_id=person.person_id,
                photo_id=photo_ids[idx],
                face_id=face_ids[idx],
            ))

    db.commit()
    logger.info("Event %s clustered → %d persons", event_id, person_count)
    return person_count


@celery_app.task(name="tasks.run_clustering")
def run_clustering_task(event_id: str) -> dict:
    db = SessionLocal()
    try:
        count = run_clustering_for_event(db, event_id)
        return {"status": "success", "event_id": event_id, "persons": count}
    except Exception as exc:
        db.rollback()
        logger.exception("Clustering failed for event %s", event_id)
        return {"status": "error", "message": str(exc)}
    finally:
        db.close()


def trigger_clustering_for_event(event_id: str) -> None:
    """Enqueue clustering asynchronously."""
    run_clustering_task.delay(event_id)
