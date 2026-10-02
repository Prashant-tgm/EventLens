"""
Alembic migration environment — wired to EventLens models and settings.

Reads DATABASE_URL from app.core.config.Settings so migrations use the
same connection string as the running application.
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

# ── Import app settings + all models so metadata is populated ────────────
from app.core.config import get_settings

# This import triggers all model registrations on Base.metadata
from app.db.base import Base  # noqa: F401 — side-effect import

# Alembic Config object (from alembic.ini)
config = context.config

# Set up loggers from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from application settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# SQLAlchemy MetaData for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emits SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connects to the database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Ensure pgvector extension exists before any migration runs
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
