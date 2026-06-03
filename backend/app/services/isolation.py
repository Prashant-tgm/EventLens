"""
Multi-tenant event isolation guards.
Every data access must pass through these checks to prevent cross-event leakage.
"""
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event, EventMember
from app.models.user import User


def check_event_access(db: Session, user: User, event_id: str) -> bool:
    """
    Returns True when the user may read data for *event_id*.
    Raises 403/404 otherwise.
    """
    if user.role == "superadmin":
        return True

    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.owner_id == user.user_id:
        return True

    membership = db.query(EventMember).filter(
        EventMember.event_id == event_id,
        EventMember.user_id == user.user_id,
    ).first()
    if membership:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this event.",
    )


def check_is_owner(db: Session, user: User, event_id: str) -> bool:
    """Raises 403 unless user owns the event (or is superadmin)."""
    if user.role == "superadmin":
        return True

    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.owner_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the Event Owner can perform this action.",
        )
    return True


def enforce_event_isolation(model_obj: Any, event_id: str) -> None:
    """
    Runtime assertion that a loaded DB row belongs to the expected event.
    Call before returning or mutating any row to prevent cross-event leakage.
    """
    if hasattr(model_obj, "event_id") and model_obj.event_id != event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity violation: event_id mismatch.",
        )
