from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="photographer", nullable=False)  # superadmin, owner, photographer
    is_active = Column(Boolean, default=True)

    # Relationships
    owned_events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")
    event_memberships = relationship("EventMember", back_populates="user", cascade="all, delete-orphan")
    uploaded_photos = relationship("Photo", back_populates="photographer")
