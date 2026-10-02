"""Initial schema — all 11 EventLens tables

Revision ID: 001_initial
Revises: None
Create Date: 2026-07-17

Captures the complete EventLens schema:
  users, events, event_members, photos, faces (with pgvector),
  persons, person_photos, invitations, uploads, search_logs, download_logs

Plus custom indexes: HNSW on faces.embedding, B-tree on log timestamps.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.String, unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=False, server_default="photographer"),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
    )

    # ── events ───────────────────────────────────────────────────────────
    op.create_table(
        "events",
        sa.Column("event_id", sa.String, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("event_type", sa.String, nullable=True),
        sa.Column("location", sa.String, nullable=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("banner_path", sa.String, nullable=True),
        sa.Column("branding_config", sa.JSON, nullable=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.user_id"), nullable=False),
    )

    # ── event_members ────────────────────────────────────────────────────
    op.create_table(
        "event_members",
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True),
        sa.Column("role", sa.String, nullable=False, server_default="photographer"),
    )

    # ── photos ───────────────────────────────────────────────────────────
    op.create_table(
        "photos",
        sa.Column("photo_id", sa.Integer, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("photographer_id", sa.Integer, sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("image_path", sa.String, nullable=False),
        sa.Column("upload_id", sa.String, nullable=True, index=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── faces (pgvector 512-D embedding) ─────────────────────────────────
    op.create_table(
        "faces",
        sa.Column("face_id", sa.Integer, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("photo_id", sa.Integer, sa.ForeignKey("photos.photo_id"), nullable=False, index=True),
        sa.Column("bbox", sa.JSON, nullable=False),
        sa.Column("quality_score", sa.Float, nullable=False),
        sa.Column("embedding", Vector(512), nullable=False),
    )

    # ── persons ──────────────────────────────────────────────────────────
    op.create_table(
        "persons",
        sa.Column("person_id", sa.Integer, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("name", sa.String, nullable=False),
    )

    # ── person_photos (composite PK) ─────────────────────────────────────
    op.create_table(
        "person_photos",
        sa.Column("person_id", sa.Integer, sa.ForeignKey("persons.person_id"), primary_key=True),
        sa.Column("photo_id", sa.Integer, sa.ForeignKey("photos.photo_id"), primary_key=True),
        sa.Column("face_id", sa.Integer, sa.ForeignKey("faces.face_id"), primary_key=True),
    )

    # ── invitations ──────────────────────────────────────────────────────
    op.create_table(
        "invitations",
        sa.Column("invitation_id", sa.Integer, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("email", sa.String, nullable=False, index=True),
        sa.Column("role", sa.String, nullable=False, server_default="photographer"),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── uploads ──────────────────────────────────────────────────────────
    op.create_table(
        "uploads",
        sa.Column("upload_id", sa.String, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("photographer_id", sa.Integer, sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("total_files", sa.Integer, server_default=sa.text("0")),
        sa.Column("processed_files", sa.Integer, server_default=sa.text("0")),
        sa.Column("faces_extracted", sa.Integer, server_default=sa.text("0")),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── search_logs ──────────────────────────────────────────────────────
    op.create_table(
        "search_logs",
        sa.Column("search_id", sa.Integer, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("matched_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("success", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── download_logs ────────────────────────────────────────────────────
    op.create_table(
        "download_logs",
        sa.Column("download_id", sa.Integer, primary_key=True, index=True),
        sa.Column("event_id", sa.String, sa.ForeignKey("events.event_id"), nullable=False, index=True),
        sa.Column("photo_id", sa.Integer, sa.ForeignKey("photos.photo_id"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ── Custom Indexes ───────────────────────────────────────────────────

    # HNSW vector index for fast cosine similarity search on face embeddings
    op.execute("""
        CREATE INDEX IF NOT EXISTS faces_embedding_hnsw
        ON faces USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    # B-tree indexes for time-range analytics queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs (created_at);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_download_logs_created_at ON download_logs (created_at);"
    )


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    op.execute("DROP INDEX IF EXISTS faces_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS idx_search_logs_created_at;")
    op.execute("DROP INDEX IF EXISTS idx_download_logs_created_at;")

    op.drop_table("download_logs")
    op.drop_table("search_logs")
    op.drop_table("uploads")
    op.drop_table("invitations")
    op.drop_table("person_photos")
    op.drop_table("persons")
    op.drop_table("faces")
    op.drop_table("photos")
    op.drop_table("event_members")
    op.drop_table("events")
    op.drop_table("users")
