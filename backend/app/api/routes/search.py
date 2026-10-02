"""
Guest selfie search endpoint.
Detects the face in the uploaded selfie, runs pgvector similarity search,
expands to person clusters, and returns pre-signed download URLs.
Every search is logged to SearchLog for real analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_download_token
from app.core.storage import get_storage_manager, StorageManager
from app.db.session import get_db
from app.models.event import Event
from app.models.face import SearchLog
from app.schemas.search import SearchResultPhoto, SelfieSearchResponse
from app.services.pipeline import extract_and_assess_faces
from app.services.vector_search import search_faces_by_vector

settings = get_settings()
router = APIRouter(prefix="/search", tags=["search"])

# Per-route rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/{event_id}", response_model=SelfieSearchResponse)
@limiter.limit("10/minute")
async def search_photos_by_selfie(
    request: Request,
    event_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage: StorageManager = Depends(get_storage_manager),
):
    """Upload a selfie → get all matching photos for this event."""
    # Validate event exists before burning CPU on face detection
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found. Please check your event code.",
        )

    img_bytes = await file.read()

    # Detect + embed the selfie
    faces_data = extract_and_assess_faces(img_bytes)
    if not faces_data:
        # Log failed search
        db.add(SearchLog(event_id=event_id, matched_count=0, success=False))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clear face detected in the selfie. Please try again with better lighting.",
        )

    # Pick the highest-quality face
    faces_data.sort(key=lambda x: x[1], reverse=True)
    _, _, selfie_embedding = faces_data[0]

    # Vector search
    matched_photos = search_faces_by_vector(db=db, event_id=event_id, query_embedding=selfie_embedding)

    # Log search
    db.add(SearchLog(event_id=event_id, matched_count=len(matched_photos), success=len(matched_photos) > 0))
    db.commit()

    results = [
        SearchResultPhoto(
            photo_id=p.photo_id,
            image_path=p.image_path,
            download_url=storage.generate_presigned_download_url(p.image_path),
            download_token=generate_download_token(event_id, p.photo_id),
        )
        for p in matched_photos
    ]

    return SelfieSearchResponse(success=True, match_count=len(results), photos=results)
