"""
FastAPI application entry-point.
Registers all routers, sets up CORS, seeds the super-admin on first start.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.routes import analytics, auth, downloads, events, health, photos, search
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base import create_db_and_tables
from app.db.session import SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="AI-Powered Event Photo Retrieval Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _seed_superadmin() -> None:
    db: Session = SessionLocal()
    try:
        if not db.query(User).filter(User.email == settings.SUPERADMIN_EMAIL).first():
            db.add(User(
                email=settings.SUPERADMIN_EMAIL,
                hashed_password=get_password_hash(settings.SUPERADMIN_PASSWORD),
                role="superadmin",
                is_active=True,
            ))
            db.commit()
            logger.info("Seeded superadmin user: %s", settings.SUPERADMIN_EMAIL)
    except Exception:
        db.rollback()
        logger.exception("Failed to seed superadmin")
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    if settings.AUTO_CREATE_TABLES:
        create_db_and_tables()
    _seed_superadmin()


# Register routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(photos.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(downloads.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
