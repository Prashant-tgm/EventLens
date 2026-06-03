from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class PhotoBase(BaseModel):
    event_id: str
    photographer_id: int
    image_path: str

class PhotoCreate(PhotoBase):
    upload_id: Optional[str] = None

class PhotoInDBBase(PhotoBase):
    photo_id: int
    upload_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Photo(PhotoInDBBase):
    pass

class PresignedUrlRequest(BaseModel):
    filenames: List[str]

class PresignedUrlResponse(BaseModel):
    filename: str
    upload_url: str
    object_key: str

class UploadInitiateResponse(BaseModel):
    upload_id: str
    urls: List[PresignedUrlResponse]
