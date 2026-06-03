"""Pydantic response schemas for analytics endpoints — all fields from real data."""
from pydantic import BaseModel


class OwnerAnalytics(BaseModel):
    total_events: int
    total_uploads: int
    total_photos: int
    total_faces: int
    total_searches: int
    successful_searches: int
    download_count: int
    search_success_rate: float


class AdminAnalytics(BaseModel):
    active_users: int
    total_events: int
    total_photos: int
    total_faces: int
    total_searches: int
    total_downloads: int
