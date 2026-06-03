"""
Import all models so they register on Base.metadata, then expose create_db_and_tables().
"""
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


def create_db_and_tables() -> None:
    """Create pgvector extension and all tables."""
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    Base.metadata.create_all(bind=engine)
