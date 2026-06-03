"""
Analytics — all values computed from real database records (SearchLog, DownloadLog, etc.).
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_active_superadmin, get_current_user
from app.db.session import get_db
from app.models.event import Event
from app.models.face import DownloadLog, Face, SearchLog, Upload
from app.models.photo import Photo
from app.models.user import User
from app.schemas.analytics import AdminAnalytics, OwnerAnalytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/owner", response_model=OwnerAnalytics)
def get_owner_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Real aggregated stats for events owned by the current user."""
    event_ids = [
        row[0]
        for row in db.query(Event.event_id).filter(Event.owner_id == current_user.user_id).all()
    ]

    if not event_ids:
        return OwnerAnalytics(
            total_events=0, total_uploads=0, total_photos=0, total_faces=0,
            total_searches=0, successful_searches=0, download_count=0,
            search_success_rate=0.0,
        )

    total_photos = db.query(func.count(Photo.photo_id)).filter(Photo.event_id.in_(event_ids)).scalar() or 0
    total_faces = db.query(func.count(Face.face_id)).filter(Face.event_id.in_(event_ids)).scalar() or 0
    total_uploads = db.query(func.count(Upload.upload_id)).filter(Upload.event_id.in_(event_ids)).scalar() or 0
    total_searches = db.query(func.count(SearchLog.search_id)).filter(SearchLog.event_id.in_(event_ids)).scalar() or 0
    successful_searches = (
        db.query(func.count(SearchLog.search_id))
        .filter(SearchLog.event_id.in_(event_ids), SearchLog.success.is_(True))
        .scalar() or 0
    )
    download_count = db.query(func.count(DownloadLog.download_id)).filter(DownloadLog.event_id.in_(event_ids)).scalar() or 0

    rate = (successful_searches / total_searches * 100.0) if total_searches > 0 else 0.0

    return OwnerAnalytics(
        total_events=len(event_ids),
        total_uploads=total_uploads,
        total_photos=total_photos,
        total_faces=total_faces,
        total_searches=total_searches,
        successful_searches=successful_searches,
        download_count=download_count,
        search_success_rate=round(rate, 1),
    )


@router.get("/admin", response_model=AdminAnalytics)
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superadmin),
):
    """System-wide stats — superadmin only. All values from real data."""
    active_users = db.query(func.count(User.user_id)).filter(User.is_active.is_(True)).scalar() or 0
    total_events = db.query(func.count(Event.event_id)).scalar() or 0
    total_photos = db.query(func.count(Photo.photo_id)).scalar() or 0
    total_faces = db.query(func.count(Face.face_id)).scalar() or 0
    total_searches = db.query(func.count(SearchLog.search_id)).scalar() or 0
    total_downloads = db.query(func.count(DownloadLog.download_id)).scalar() or 0

    return AdminAnalytics(
        active_users=active_users,
        total_events=total_events,
        total_photos=total_photos,
        total_faces=total_faces,
        total_searches=total_searches,
        total_downloads=total_downloads,
    )
