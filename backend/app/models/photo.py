from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Photo(Base):
    __tablename__ = "photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.event_id"), nullable=False, index=True)
    photographer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    image_path = Column(String, nullable=False)  # S3/MinIO key
    upload_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    event = relationship("Event", back_populates="photos")
    photographer = relationship("User", back_populates="uploaded_photos")
    faces = relationship("Face", back_populates="photo", cascade="all, delete-orphan")
    person_photos = relationship("PersonPhoto", back_populates="photo", cascade="all, delete-orphan")
