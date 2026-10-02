"""
Auth endpoint tests — registration, login, profile.
"""
import pytest


class TestRegister:
    """POST /api/v1/auth/register"""

    def test_register_new_user(self, client):
        """Register a brand-new user — should succeed."""
        resp = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "StrongPass123!",
            "role": "owner",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "owner"
        assert data["is_active"] is True
        assert "user_id" in data

    def test_register_duplicate_email(self, client, test_owner):
        """Registering with an existing email should return 400."""
        resp = client.post("/api/v1/auth/register", json={
            "email": "owner@test.com",  # already exists from test_owner
            "password": "AnyPassword123!",
            "role": "owner",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_default_role(self, client):
        """Omitting 'role' should default to 'photographer'."""
        resp = client.post("/api/v1/auth/register", json={
            "email": "defaultrole@test.com",
            "password": "Pass123!",
        })
        assert resp.status_code == 200
        assert resp.json()["role"] == "photographer"


class TestLogin:
    """POST /api/v1/auth/token"""

    def test_login_valid_credentials(self, client, test_owner):
        """Valid email + password should return a JWT."""
        resp = client.post("/api/v1/auth/token", data={
            "username": "owner@test.com",
            "password": "TestPassword123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_owner):
        """Wrong password should return 401."""
        resp = client.post("/api/v1/auth/token", data={
            "username": "owner@test.com",
            "password": "WrongPassword!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Non-existent user should return 401."""
        resp = client.post("/api/v1/auth/token", data={
            "username": "ghost@test.com",
            "password": "Whatever123!",
        })
        assert resp.status_code == 401


class TestProfile:
    """GET /api/v1/auth/me"""

    def test_get_me_authenticated(self, client, owner_headers):
        """Authenticated user should get their profile."""
        resp = client.get("/api/v1/auth/me", headers=owner_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "owner@test.com"
        assert data["role"] == "owner"

    def test_get_me_no_token(self, client):
        """Missing auth token should return 401."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Invalid JWT should return 401."""
        resp = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer totally.invalid.token"
        })
        assert resp.status_code == 401
