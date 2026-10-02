"""
Event CRUD, team invitations, invitation acceptance, stats, and cluster visualization.
"""
import random
from datetime import datetime
from typing import List

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.event import Event, EventMember
from app.models.face import Face, Invitation, Person, PersonPhoto, Upload
from app.models.photo import Photo
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
    """Invite a photographer by email — sends notification via Resend if configured."""
    check_is_owner(db, current_user, event_id)

    existing = db.query(User).filter(User.email == invite_in.email).first()
    if existing:
        already = db.query(EventMember).filter(
            EventMember.event_id == event_id,
            EventMember.user_id == existing.user_id,
        ).first()
        if already:
            raise HTTPException(status_code=400, detail="Already a member of this event")

    invitation = Invitation(
        event_id=event_id, email=invite_in.email,
        role=invite_in.role, status="pending",
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send email notification (best-effort — invite is saved even if email fails)
    from app.services.email import send_invitation_email

    event = db.query(Event).filter(Event.event_id == event_id).first()
    event_name = event.name if event else event_id

    email_sent = send_invitation_email(
        to_email=invite_in.email,
        event_name=event_name,
        inviter_email=current_user.email,
        invitation_id=invitation.invitation_id,
    )

    return {
        "status": "success",
        "message": f"Invitation sent to {invite_in.email}",
        "email_sent": email_sent,
        "invitation_id": invitation.invitation_id,
    }


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


# ---------------------------------------------------------------------------
# Event Stats
# ---------------------------------------------------------------------------

@router.get("/{event_id}/stats")
def get_event_stats(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate statistics for an event: photos, batches, faces, persons."""
    check_event_access(db, current_user, event_id)

    total_photos = db.query(Photo).filter(Photo.event_id == event_id).count()
    total_batches = db.query(Upload).filter(Upload.event_id == event_id).count()
    total_faces = db.query(Face).filter(Face.event_id == event_id).count()
    total_persons = db.query(Person).filter(Person.event_id == event_id).count()
    processing_batches = (
        db.query(Upload)
        .filter(Upload.event_id == event_id, Upload.status.in_(["pending", "processing"]))
        .count()
    )

    return {
        "total_photos": total_photos,
        "total_batches": total_batches,
        "total_faces": total_faces,
        "total_persons": total_persons,
        "processing_batches": processing_batches,
    }


# ---------------------------------------------------------------------------
# Cluster Visualization (t-SNE projection of face embeddings)
# ---------------------------------------------------------------------------

@router.get("/{event_id}/clusters")
def get_event_clusters(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """2-D t-SNE projection of every face embedding in the event, grouped by person."""
    check_event_access(db, current_user, event_id)

    # 1. Fetch all faces for the event
    faces = db.query(Face).filter(Face.event_id == event_id).all()
    n_faces = len(faces)

    # 2. Build a face_id → person_id lookup from PersonPhoto
    person_photo_rows = (
        db.query(PersonPhoto)
        .join(Person, PersonPhoto.person_id == Person.person_id)
        .filter(Person.event_id == event_id)
        .all()
    )
    face_to_person: dict[int, int] = {pp.face_id: pp.person_id for pp in person_photo_rows}

    # 3. Fetch all persons for the event
    persons = db.query(Person).filter(Person.event_id == event_id).all()
    person_map: dict[int, str] = {p.person_id: p.name for p in persons}
    total_persons = len(persons)

    # 4. Compute 2-D coordinates via t-SNE (or zeros when < 2 faces)
    if n_faces >= 2:
        from sklearn.manifold import TSNE  # already available

        embeddings = np.array([list(f.embedding) for f in faces], dtype=np.float64)
        # Normalize embeddings (L2-norm per row)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # avoid division by zero
        embeddings = embeddings / norms

        perplexity = min(30, n_faces - 1)
        coords = TSNE(
            n_components=2,
            perplexity=perplexity,
            random_state=42,
        ).fit_transform(embeddings)
    else:
        coords = np.zeros((n_faces, 2))

    # 5. Build per-person and unclustered lists
    person_faces: dict[int, list] = {pid: [] for pid in person_map}
    unclustered: list[dict] = []

    for idx, face in enumerate(faces):
        entry = {
            "face_id": face.face_id,
            "photo_id": face.photo_id,
            "x": float(coords[idx, 0]),
            "y": float(coords[idx, 1]),
            "quality": float(face.quality_score),
        }
        pid = face_to_person.get(face.face_id)
        if pid is not None and pid in person_faces:
            person_faces[pid].append(entry)
        else:
            unclustered.append(entry)

    persons_out = [
        {
            "person_id": pid,
            "name": person_map[pid],
            "face_count": len(face_list),
            "faces": face_list,
        }
        for pid, face_list in person_faces.items()
    ]

    return {
        "total_faces": n_faces,
        "total_persons": total_persons,
        "persons": persons_out,
        "unclustered": unclustered,
    }
