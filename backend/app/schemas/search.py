from typing import List
from pydantic import BaseModel

class SearchResultPhoto(BaseModel):
    photo_id: int
    image_path: str
    download_url: str

class SelfieSearchResponse(BaseModel):
    success: bool
    match_count: int
    photos: List[SearchResultPhoto]
