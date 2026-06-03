"""
Application settings loaded from environment variables via pydantic-settings.
Uses functools.lru_cache to avoid re-reading .env on every dependency injection.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "EventSnap AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # ── Security ─────────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:password123@localhost:5432/eventsnap"
    AUTO_CREATE_TABLES: bool = True

    # ── Redis / Celery ───────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Object Storage ───────────────────────────────────────────────────
    STORAGE_PROVIDER: str = "minio"  # "minio" or "s3"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadminpassword"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "eventsnap"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "eventsnap-photos"

    # ── Seed Super-Admin ─────────────────────────────────────────────────
    SUPERADMIN_EMAIL: str = "admin@eventsnap.ai"
    SUPERADMIN_PASSWORD: str = "AdminSecurePassword123!"

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["*"]

    # ── AI Pipeline Tuning ───────────────────────────────────────────────
    FACE_MIN_SIZE_PX: int = 40        # discard faces smaller than this
    FACE_BLUR_THRESHOLD: float = 50.0 # Laplacian variance below this → skip
    SEARCH_SIMILARITY_THRESHOLD: float = 0.55
    SEARCH_MAX_RESULTS: int = 50

    @property
    def storage_root(self) -> Path:
        root = Path(__file__).resolve().parent.parent.parent / "storage"
        root.mkdir(parents=True, exist_ok=True)
        return root


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton so Settings is read once per process."""
    return Settings()
