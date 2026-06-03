"""
pgvector cosine-similarity search + person-cluster expansion.

Given a query embedding and event_id, returns a de-duplicated list of Photo objects.
"""
from typing import List

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.storage import get_storage_manager
from app.models.face import Face, PersonPhoto
from app.models.photo import Photo

settings = get_settings()


def search_faces_by_vector(
    db: Session,
    event_id: str,
    query_embedding: List[float],
    threshold: float | None = None,
    limit: int | None = None,
) -> List[Photo]:
    """
    1. Query faces within *event_id* by cosine distance.
    2. Find the person clusters those faces belong to.
    3. Expand to all photos in those clusters.
    4. Return de-duplicated Photo list (still scoped to event_id).
    """
    threshold = threshold or settings.SEARCH_SIMILARITY_THRESHOLD
    limit = limit or settings.SEARCH_MAX_RESULTS
    max_distance = 1.0 - threshold

    distance_expr = Face.embedding.cosine_distance(query_embedding)

    rows = (
        db.query(Face, distance_expr.label("distance"))
        .filter(Face.event_id == event_id)
        .filter(distance_expr < max_distance)
        .order_by("distance")
        .limit(limit)
        .all()
    )

    if not rows:
        return []

    matched_face_ids = [r[0].face_id for r in rows]
    direct_photo_ids = {r[0].photo_id for r in rows}

    # Expand via person clusters
    person_ids = {
        m.person_id
        for m in db.query(PersonPhoto).filter(PersonPhoto.face_id.in_(matched_face_ids)).all()
    }

    cluster_photo_ids: set[int] = set()
    if person_ids:
        cluster_photo_ids = {
            m.photo_id
            for m in db.query(PersonPhoto).filter(PersonPhoto.person_id.in_(person_ids)).all()
        }

    all_photo_ids = list(direct_photo_ids | cluster_photo_ids)
    if not all_photo_ids:
        return []

    return (
        db.query(Photo)
        .filter(Photo.photo_id.in_(all_photo_ids), Photo.event_id == event_id)
        .all()
    )
