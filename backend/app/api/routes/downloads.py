"""
Photo download endpoint — generates a pre-signed URL and logs the download.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.storage import StorageManager, get_storage_manager
from app.db.session import get_db
from app.models.face import DownloadLog
from app.models.photo import Photo

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.get("/{event_id}/{photo_id}")
def download_photo(
    event_id: str,
    photo_id: int,
    db: Session = Depends(get_db),
    storage: StorageManager = Depends(get_storage_manager),
):
    """
    Returns a pre-signed download URL for a single photo and logs the download.
    This is the endpoint guests use from the UI to actually download a matched photo.
    """
    photo = db.query(Photo).filter(Photo.photo_id == photo_id, Photo.event_id == event_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    url = storage.generate_presigned_download_url(photo.image_path)

    db.add(DownloadLog(event_id=event_id, photo_id=photo_id))
    db.commit()

    return {"download_url": url}
