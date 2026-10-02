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


@router.get("/trends")
def get_analytics_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Real time-series trend data for searches and downloads."""
    from datetime import datetime, timedelta
    from sqlalchemy import cast, Date

    start_date = datetime.utcnow() - timedelta(days=days)

    # Get event IDs for this user
    if current_user.role == "superadmin":
        event_filter = True  # all events
    else:
        event_ids = [
            row[0]
            for row in db.query(Event.event_id).filter(Event.owner_id == current_user.user_id).all()
        ]
        if not event_ids:
            return {"dates": [], "searches": [], "downloads": []}
        event_filter = SearchLog.event_id.in_(event_ids)

    # Search trends
    search_rows = (
        db.query(
            cast(SearchLog.created_at, Date).label("date"),
            func.count(SearchLog.search_id).label("count"),
        )
        .filter(SearchLog.created_at >= start_date)
        .filter(event_filter)
        .group_by(cast(SearchLog.created_at, Date))
        .order_by(cast(SearchLog.created_at, Date))
        .all()
    )

    # Download trends
    if current_user.role == "superadmin":
        dl_event_filter = True
    else:
        dl_event_filter = DownloadLog.event_id.in_(event_ids)

    download_rows = (
        db.query(
            cast(DownloadLog.created_at, Date).label("date"),
            func.count(DownloadLog.download_id).label("count"),
        )
        .filter(DownloadLog.created_at >= start_date)
        .filter(dl_event_filter)
        .group_by(cast(DownloadLog.created_at, Date))
        .order_by(cast(DownloadLog.created_at, Date))
        .all()
    )

    # Build aligned date series
    all_dates = sorted(set(
        [str(r.date) for r in search_rows] +
        [str(r.date) for r in download_rows]
    ))
    search_map = {str(r.date): r.count for r in search_rows}
    download_map = {str(r.date): r.count for r in download_rows}

    return {
        "dates": all_dates,
        "searches": [search_map.get(d, 0) for d in all_dates],
        "downloads": [download_map.get(d, 0) for d in all_dates],
    }
