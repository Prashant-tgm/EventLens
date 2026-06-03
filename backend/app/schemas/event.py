from datetime import date
from typing import Optional, Any, Dict
from pydantic import BaseModel

class EventBase(BaseModel):
    name: str
    date: date
    event_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    branding_config: Optional[Dict[str, Any]] = None

class EventCreate(EventBase):
    event_id: str  # e.g., EVT-2026-0001 (generated on client or seeded)

class EventUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    banner_path: Optional[str] = None
    branding_config: Optional[Dict[str, Any]] = None

class EventInDBBase(EventBase):
    event_id: str
    owner_id: int
    banner_path: Optional[str] = None

    class Config:
        from_attributes = True

class Event(EventInDBBase):
    pass

class EventMemberInvite(BaseModel):
    email: str
    role: Optional[str] = "photographer"
