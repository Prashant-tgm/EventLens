"""
Face-centric models: Face embeddings, Person clusters, Invitations, Uploads, SearchLogs.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.base_class import Base


class Face(Base):
    __tablename__ = "faces"

    face_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    photo_id = Column(Integer, ForeignKey("photos.photo_id"), nullable=False, index=True)
    bbox = Column(JSON, nullable=False)              # [x, y, w, h]
    quality_score = Column(Float, nullable=False)
    embedding = Column(Vector(512), nullable=False)  # 512-D ArcFace embedding

    event = relationship("Event", back_populates="faces")
    photo = relationship("Photo", back_populates="faces")
    person_photos = relationship("PersonPhoto", back_populates="face", cascade="all, delete-orphan")


class Person(Base):
    __tablename__ = "persons"

    person_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g. Person_001

    event = relationship("Event", back_populates="persons")
    photos = relationship("PersonPhoto", back_populates="person", cascade="all, delete-orphan")


class PersonPhoto(Base):
    __tablename__ = "person_photos"

    person_id = Column(Integer, ForeignKey("persons.person_id"), primary_key=True)
    photo_id = Column(Integer, ForeignKey("photos.photo_id"), primary_key=True)
    face_id = Column(Integer, ForeignKey("faces.face_id"), primary_key=True)

    person = relationship("Person", back_populates="photos")
    photo = relationship("Photo", back_populates="person_photos")
    face = relationship("Face", back_populates="person_photos")


class Invitation(Base):
    __tablename__ = "invitations"

    invitation_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(String, default="photographer", nullable=False)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    event = relationship("Event", back_populates="invitations")


class Upload(Base):
    __tablename__ = "uploads"

    upload_id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    photographer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    faces_extracted = Column(Integer, default=0)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    event = relationship("Event", back_populates="uploads")


class SearchLog(Base):
    """Tracks every guest selfie search — used by analytics (no mocks)."""
    __tablename__ = "search_logs"

    search_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    matched_count = Column(Integer, nullable=False, default=0)
    success = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())

    event = relationship("Event", back_populates="search_logs")


class DownloadLog(Base):
    """Tracks photo downloads — used by analytics (no mocks)."""
    __tablename__ = "download_logs"

    download_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    photo_id = Column(Integer, ForeignKey("photos.photo_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    event = relationship("Event", back_populates="download_logs")
