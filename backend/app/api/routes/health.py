"""
Health-check endpoint — verifies DB, Redis, Storage, and Celery worker status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    checks = {"service": "EventLens AI Backend"}

    # Database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"

    # Redis + Queue depth
    try:
        import redis
        from app.core.config import get_settings
        r = redis.from_url(get_settings().REDIS_URL, socket_connect_timeout=2)
        r.ping()
        checks["redis"] = "ok"
        # Check Celery queue depth
        queue_depth = r.llen("celery")
        checks["queue_depth"] = queue_depth
        checks["worker"] = "ok" if queue_depth < 100 else "backlogged"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
        checks["queue_depth"] = -1
        checks["worker"] = "unknown"

    # Storage
    try:
        from app.core.storage import get_storage_manager
        mgr = get_storage_manager()
        mgr.s3.head_bucket(Bucket=mgr.bucket)
        checks["storage"] = "ok"
    except Exception as exc:
        checks["storage"] = f"error: {exc}"

    all_ok = all(
        v == "ok"
        for k, v in checks.items()
        if k not in ("service", "queue_depth")
    )
    checks["status"] = "healthy" if all_ok else "degraded"
    return checks
