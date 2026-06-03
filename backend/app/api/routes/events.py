"""
Event CRUD, team invitations, and invitation acceptance.
"""
import random
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.event import Event, EventMember
from app.models.face import Invitation
from app.models.user import User
from app.schemas.event import (
    Event as EventSchema,
    EventBase,
    EventMemberInvite,
    EventUpdate,
)
from app.services.isolation import check_event_access, check_is_owner

router = APIRouter(prefix="/events", tags=["events"])


def _generate_event_id(db: Session) -> str:
    year = datetime.now().year
    while True:
        code = f"EVT-{year}-{random.randint(1000, 9999)}"
        if not db.query(Event).filter(Event.event_id == code).first():
            return code


@router.post("/", response_model=EventSchema)
def create_event(
    event_in: EventBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new event (owners and superadmins only)."""
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners or admins can create events")

    event = Event(
        event_id=_generate_event_id(db),
        name=event_in.name,
        date=event_in.date,
        event_type=event_in.event_type,
        location=event_in.location,
        description=event_in.description,
        branding_config=event_in.branding_config,
        owner_id=current_user.user_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=List[EventSchema])
def list_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List events the caller owns or is a member of."""
    if current_user.role == "superadmin":
        return db.query(Event).all()

    owned = db.query(Event).filter(Event.owner_id == current_user.user_id).all()
    member_ids = [
        m.event_id
        for m in db.query(EventMember).filter(EventMember.user_id == current_user.user_id).all()
    ]
    member_of = db.query(Event).filter(Event.event_id.in_(member_ids)).all() if member_ids else []

    merged = {e.event_id: e for e in owned + member_of}
    return list(merged.values())


@router.get("/{event_id}", response_model=EventSchema)
def get_event_details(event_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_event_access(db, current_user, event_id)
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventSchema)
def update_event(
    event_id: str,
    event_update: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_is_owner(db, current_user, event_id)
    event = db.query(Event).filter(Event.event_id == event_id).first()

    for field, value in event_update.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/invite")
def invite_photographer(
    event_id: str,
    invite_in: EventMemberInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a photographer by email."""
    check_is_owner(db, current_user, event_id)

    existing = db.query(User).filter(User.email == invite_in.email).first()
    if existing:
        already = db.query(EventMember).filter(
            EventMember.event_id == event_id,
            EventMember.user_id == existing.user_id,
        ).first()
        if already:
            raise HTTPException(status_code=400, detail="Already a member of this event")

    db.add(Invitation(event_id=event_id, email=invite_in.email, role=invite_in.role, status="pending"))
    db.commit()
    return {"status": "success", "message": f"Invitation sent to {invite_in.email}"}


@router.post("/accept-invite/{invitation_id}")
def accept_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(Invitation).filter(Invitation.invitation_id == invitation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if inv.email != current_user.email:
        raise HTTPException(status_code=403, detail="This invitation was not sent to your email")

    if not db.query(EventMember).filter(
        EventMember.event_id == inv.event_id,
        EventMember.user_id == current_user.user_id,
    ).first():
        db.add(EventMember(event_id=inv.event_id, user_id=current_user.user_id, role=inv.role))

    inv.status = "accepted"
    db.commit()
    return {"status": "success", "event_id": inv.event_id}
