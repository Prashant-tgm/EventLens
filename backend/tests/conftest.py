"""
Pytest fixtures for EventLens backend tests.

Uses a REAL PostgreSQL database (with pgvector) for accurate integration testing.
Requires a running PostgreSQL instance with the pgvector extension installed.

Connection string is read from TEST_DATABASE_URL env var, falling back to a
dedicated test database on the default local Postgres instance.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core import security
from app.db.base_class import Base
# Import all models so metadata is populated
from app.db.base import (  # noqa: F401
    User, Event, EventMember, Photo,
    Face, Person, PersonPhoto,
    Invitation, Upload,
    SearchLog, DownloadLog,
)
from app.db.session import get_db
from app.main import app


# ── Test Database ────────────────────────────────────────────────────────

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:password123@localhost:5432/eventlens_test",
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine,
)


# ── Session-Scoped: Create/Drop Tables Once Per Test Session ─────────────

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create pgvector extension and all tables at the start of the test run,
    and drop everything at the end."""
    with test_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ── Function-Scoped: Clean Database Between Tests ────────────────────────

@pytest.fixture(autouse=True)
def db_session():
    """Provide a clean database session per test.

    Uses a transaction that is rolled back after each test for isolation
    without the overhead of dropping/creating tables every time.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    # Override the FastAPI dependency
    app.dependency_overrides[get_db] = lambda: session

    yield session

    # Rollback everything done during the test
    session.close()
    transaction.rollback()
    connection.close()

    app.dependency_overrides.clear()


# ── Test Client ──────────────────────────────────────────────────────────

@pytest.fixture
def client(db_session):
    """FastAPI TestClient wired to the test database session."""
    with TestClient(app) as c:
        yield c


# ── User Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def test_owner(db_session):
    """Create an owner user for testing."""
    user = User(
        email="owner@test.com",
        hashed_password=security.get_password_hash("TestPassword123!"),
        role="owner",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()  # flush so user_id is assigned
    return user


@pytest.fixture
def test_photographer(db_session):
    """Create a photographer user for testing."""
    user = User(
        email="photo@test.com",
        hashed_password=security.get_password_hash("TestPassword123!"),
        role="photographer",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_superadmin(db_session):
    """Create a superadmin user for testing."""
    user = User(
        email="admin@test.com",
        hashed_password=security.get_password_hash("AdminPassword123!"),
        role="superadmin",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


# ── Auth Header Helpers ──────────────────────────────────────────────────

def _auth_headers(email: str) -> dict:
    """Build Authorization header with a valid JWT for the given email."""
    token = security.create_access_token(subject=email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def owner_headers(test_owner) -> dict:
    """Authorization headers for the test owner."""
    return _auth_headers(test_owner.email)


@pytest.fixture
def photographer_headers(test_photographer) -> dict:
    """Authorization headers for the test photographer."""
    return _auth_headers(test_photographer.email)


@pytest.fixture
def superadmin_headers(test_superadmin) -> dict:
    """Authorization headers for the test superadmin."""
    return _auth_headers(test_superadmin.email)


# ── Event Fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def test_event(db_session, test_owner):
    """Create a test event owned by test_owner."""
    from datetime import date

    event = Event(
        event_id="EVT-2026-0001",
        name="Test Wedding",
        date=date(2026, 12, 25),
        event_type="Wedding",
        location="New York",
        description="A test event for unit testing",
        owner_id=test_owner.user_id,
    )
    db_session.add(event)
    db_session.flush()
    return event
