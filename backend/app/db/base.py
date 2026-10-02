"""
Import all models so they register on Base.metadata, then expose create_db_and_tables().
"""
import logging

from app.db.base_class import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.event import Event, EventMember  # noqa: F401
from app.models.photo import Photo  # noqa: F401
from app.models.face import (  # noqa: F401
    Face, Person, PersonPhoto,
    Invitation, Upload,
    SearchLog, DownloadLog,
)

from app.db.session import engine

logger = logging.getLogger(__name__)


def create_db_and_tables() -> None:
    """Create pgvector extension, HNSW index, and all tables.

    WARNING: This uses raw CREATE TABLE IF NOT EXISTS, which cannot ALTER
    existing columns. Use Alembic migrations in production instead:
        cd backend && alembic upgrade head
    """
    logger.warning(
        "AUTO_CREATE_TABLES is True — using raw Base.metadata.create_all(). "
        "For production, set AUTO_CREATE_TABLES=False and use: alembic upgrade head"
    )
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    Base.metadata.create_all(bind=engine)

    # Create HNSW vector index for fast cosine similarity search
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS faces_embedding_hnsw
            ON faces USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs (created_at);"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_download_logs_created_at ON download_logs (created_at);"
        ))

