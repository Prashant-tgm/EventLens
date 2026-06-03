"""
Event and EventMember models.
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)  # EVT-2026-XXXX
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    event_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    banner_path = Column(String, nullable=True)
    branding_config = Column(JSON, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # relationships
    owner = relationship("User", back_populates="owned_events")
    members = relationship("EventMember", back_populates="event", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="event", cascade="all, delete-orphan")
    faces = relationship("Face", back_populates="event", cascade="all, delete-orphan")
    persons = relationship("Person", back_populates="event", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="event", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="event", cascade="all, delete-orphan")
    search_logs = relationship("SearchLog", back_populates="event", cascade="all, delete-orphan")
    download_logs = relationship("DownloadLog", back_populates="event", cascade="all, delete-orphan")


class EventMember(Base):
    __tablename__ = "event_members"

    event_id = Column(String, ForeignKey("events.event_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    role = Column(String, default="photographer", nullable=False)

    event = relationship("Event", back_populates="members")
    user = relationship("User", back_populates="event_memberships")
