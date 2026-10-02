"""
Event CRUD and invitation endpoint tests.
"""
import pytest
from datetime import date


class TestCreateEvent:
    """POST /api/v1/events/"""

    def test_create_event_owner(self, client, owner_headers):
        """Owners can create events."""
        resp = client.post("/api/v1/events/", json={
            "name": "Summer Gala",
            "date": "2026-08-15",
            "event_type": "Corporate",
            "location": "San Francisco",
            "description": "Annual summer event",
        }, headers=owner_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Summer Gala"
        assert data["event_id"].startswith("EVT-")
        assert data["event_type"] == "Corporate"

    def test_create_event_photographer_forbidden(self, client, photographer_headers):
        """Photographers cannot create events."""
        resp = client.post("/api/v1/events/", json={
            "name": "Should Fail",
            "date": "2026-08-15",
        }, headers=photographer_headers)
        assert resp.status_code == 403

    def test_create_event_superadmin(self, client, superadmin_headers):
        """Superadmins can create events."""
        resp = client.post("/api/v1/events/", json={
            "name": "Admin Event",
            "date": "2026-09-01",
        }, headers=superadmin_headers)
        assert resp.status_code == 200


class TestListEvents:
    """GET /api/v1/events/"""

    def test_list_events_owner(self, client, owner_headers, test_event):
        """Owner should see their events."""
        resp = client.get("/api/v1/events/", headers=owner_headers)
        assert resp.status_code == 200
        events = resp.json()
        assert len(events) >= 1
        assert any(e["event_id"] == "EVT-2026-0001" for e in events)


class TestGetEvent:
    """GET /api/v1/events/{event_id}"""

    def test_get_event_details(self, client, owner_headers, test_event):
        """Owner can fetch event details."""
        resp = client.get(f"/api/v1/events/{test_event.event_id}", headers=owner_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Wedding"
        assert data["event_id"] == "EVT-2026-0001"

    def test_get_event_no_access(self, client, photographer_headers, test_event):
        """Non-member user should be denied access."""
        resp = client.get(f"/api/v1/events/{test_event.event_id}", headers=photographer_headers)
        assert resp.status_code == 403


class TestUpdateEvent:
    """PUT /api/v1/events/{event_id}"""

    def test_update_event_owner(self, client, owner_headers, test_event):
        """Owner can update their event."""
        resp = client.put(f"/api/v1/events/{test_event.event_id}", json={
            "name": "Updated Wedding Name",
            "location": "Brooklyn",
        }, headers=owner_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Wedding Name"
        assert data["location"] == "Brooklyn"

    def test_update_event_non_owner(self, client, photographer_headers, test_event):
        """Non-owner cannot update event."""
        resp = client.put(f"/api/v1/events/{test_event.event_id}", json={
            "name": "Hacker",
        }, headers=photographer_headers)
        assert resp.status_code == 403


class TestInvitation:
    """POST /api/v1/events/{event_id}/invite and accept flow."""

    def test_invite_member(self, client, owner_headers, test_event):
        """Owner can invite a photographer by email."""
        resp = client.post(f"/api/v1/events/{test_event.event_id}/invite", json={
            "email": "photographer@example.com",
            "role": "photographer",
        }, headers=owner_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "invitation_id" in data
        # email_sent may be False if Resend is not configured — that's expected
        assert "email_sent" in data

    def test_invite_duplicate_member(self, client, owner_headers, test_event, db_session):
        """Inviting an already-member should return 400."""
        from app.models.event import EventMember
        from app.models.user import User
        from app.core import security as sec

        # Create user and add as member
        user = User(
            email="existing@test.com",
            hashed_password=sec.get_password_hash("pass"),
            role="photographer",
        )
        db_session.add(user)
        db_session.flush()
        db_session.add(EventMember(
            event_id=test_event.event_id,
            user_id=user.user_id,
            role="photographer",
        ))
        db_session.flush()

        resp = client.post(f"/api/v1/events/{test_event.event_id}/invite", json={
            "email": "existing@test.com",
            "role": "photographer",
        }, headers=owner_headers)
        assert resp.status_code == 400


class TestEventStats:
    """GET /api/v1/events/{event_id}/stats"""

    def test_event_stats(self, client, owner_headers, test_event):
        """Stats endpoint should return counts (all zero for fresh event)."""
        resp = client.get(f"/api/v1/events/{test_event.event_id}/stats", headers=owner_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_photos"] == 0
        assert data["total_batches"] == 0
        assert data["total_faces"] == 0
        assert data["total_persons"] == 0
        assert data["processing_batches"] == 0
