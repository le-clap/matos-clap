"""Tests for authentication endpoints."""

import logging
from unittest.mock import AsyncMock, patch

from models.enums import AccessLevel
from tests.conftest import make_token, make_user


def test_login_redirects_to_cla(client):
    r = client.get("/api/auth/login", follow_redirects=False)
    assert r.status_code in (301, 302, 307, 308)
    assert "centralelilleassos" in r.headers["location"]


def test_callback_invalid_ticket_returns_401(client):
    with patch("routers.auth.validate_ticket", new=AsyncMock(return_value=None)):
        r = client.get("/api/auth/cla/callback?ticket=bad_ticket")
    assert r.status_code == 401


def test_callback_valid_ticket_creates_user_and_session(client, session):
    payload = {
        "username": "new_student",
        "firstName": "New",
        "lastName": "Student",
        "emailSchool": "new.student@centralelille.fr",
    }
    with patch("routers.auth.validate_ticket", new=AsyncMock(return_value=payload)):
        r = client.get("/api/auth/cla/callback?ticket=good_ticket", follow_redirects=False)

    assert r.status_code in (301, 302, 307, 308)
    assert "session_id" in r.cookies

    # User was persisted
    client.cookies = {"session_id": r.cookies["session_id"]}
    me_r = client.get("/api/users/me")
    assert me_r.status_code == 200
    data = me_r.json()
    assert data["username"] == "new_student"
    assert data["email"] == "new.student@centralelille.fr"


def test_callback_updates_existing_user(client, session):
    """A second login with the same username updates name/email in place."""
    existing = make_user(session, AccessLevel.USER, 99)

    payload = {
        "username": existing.username,
        "firstName": "Updated",
        "lastName": "Name",
        "emailSchool": "updated@centralelille.fr",
    }
    with patch("routers.auth.validate_ticket", new=AsyncMock(return_value=payload)):
        r = client.get("/api/auth/cla/callback?ticket=update_ticket", follow_redirects=False)

    assert r.status_code in (301, 302, 307, 308)
    client.cookies = {"session_id": r.cookies["session_id"]}
    me_r = client.get("/api/users/me")
    data = me_r.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "updated@centralelille.fr"


def test_get_me_with_cookie(client, session):
    user = make_user(session, AccessLevel.USER, 1)
    token = make_token(session, user)

    client.cookies = {"session_id": token}
    r = client.get("/api/users/me")
    assert r.status_code == 200
    assert r.json()["username"] == user.username


def test_get_me_with_bearer_token(client, session):
    user = make_user(session, AccessLevel.USER, 2)
    token = make_token(session, user)

    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["id"] == user.id


def test_get_me_unauthenticated_returns_401(client):
    r = client.get("/api/users/me")
    assert r.status_code == 401


def test_get_me_expired_session_returns_401(client, session):
    user = make_user(session, AccessLevel.USER, 3)
    expired_token = make_token(session, user, expired=True)

    client.cookies = {"session_id": expired_token}
    r = client.get("/api/users/me")
    assert r.status_code == 401


def test_logout_clears_session(client, session):
    user = make_user(session, AccessLevel.USER, 4)
    token = make_token(session, user)

    client.cookies = {"session_id": token}
    r = client.post("/api/auth/logout", follow_redirects=False)
    assert r.status_code in (301, 302, 307, 308)

    # Cookie should be cleared (max_age=0 or empty value)
    assert r.cookies.get("session_id", "") in ("", None) or "session_id" not in r.cookies

    # Token no longer valid
    client.cookies = {"session_id": token}
    me_r = client.get("/api/users/me")
    assert me_r.status_code == 401


def test_logout_without_session_is_graceful(client):
    """Logout without a session cookie should still redirect cleanly."""
    r = client.post("/api/auth/logout", follow_redirects=False)
    assert r.status_code in (301, 302, 307, 308)


def test_permission_denied_is_logged(client, session, caplog):
    user = make_user(session, AccessLevel.USER, 5)
    token = make_token(session, user)

    with caplog.at_level(logging.WARNING):
        r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 403
    assert "auth.permission_denied" in caplog.text
