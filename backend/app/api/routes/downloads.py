"""
Photo download endpoint — validates HMAC token, generates a pre-signed URL,
and logs the download.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import verify_download_token
from app.core.storage import StorageManager, get_storage_manager
from app.db.session import get_db
from app.models.face import DownloadLog
from app.models.photo import Photo

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.get("/{event_id}/{photo_id}")
def download_photo(
    event_id: str,
    photo_id: int,
    token: str = Query(..., description="HMAC download token from search results"),
    db: Session = Depends(get_db),
    storage: StorageManager = Depends(get_storage_manager),
):
    """
    Returns a pre-signed download URL for a single photo.
    Requires a valid HMAC token (generated during search) to prevent
    unauthorized enumeration of photo IDs.
    """
    if not verify_download_token(event_id, photo_id, token):
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired download token. Please search again.",
        )

    photo = db.query(Photo).filter(
        Photo.photo_id == photo_id,
        Photo.event_id == event_id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    url = storage.generate_presigned_download_url(photo.image_path)

    db.add(DownloadLog(event_id=event_id, photo_id=photo_id))
    db.commit()

    return {"download_url": url}
