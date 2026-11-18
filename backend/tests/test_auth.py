"""Tests for authentication endpoints."""

import logging
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from authlib.integrations.base_client import OAuthError

from models.enums import AccessLevel
from services.oidc import oauth
from tests.conftest import make_token, make_user

METADATA = {
    "issuer": "https://idp.test/auth",
    "authorization_endpoint": "https://idp.test/auth/authorize/",
    "token_endpoint": "https://idp.test/auth/token/",
    "end_session_endpoint": "https://idp.test/auth/logout/",
}


@pytest.fixture(autouse=True)
def _static_oidc_metadata():
    """Preload discovery metadata so tests never hit the network."""
    oauth.cla.server_metadata = {**METADATA, "_loaded_at": 1}
    yield
    oauth.cla.server_metadata = {}


def test_login_redirects_with_pkce(client):
    r = client.get("/api/auth/login", follow_redirects=False)
    assert r.status_code == 302
    q = parse_qs(urlparse(r.headers["location"]).query)
    assert r.headers["location"].startswith(METADATA["authorization_endpoint"])
    assert q["code_challenge_method"] == ["S256"]
    assert "code_challenge" in q and "state" in q and "nonce" in q


def _callback(client, userinfo):
    token = {"userinfo": userinfo}
    with patch.object(oauth.cla, "authorize_access_token", new=AsyncMock(return_value=token)):
        return client.get("/api/auth/callback?code=c&state=s", follow_redirects=False)


def test_callback_failure_returns_401(client):
    with patch.object(oauth.cla, "authorize_access_token", new=AsyncMock(side_effect=OAuthError("access_denied"))):
        r = client.get("/api/auth/callback?error=access_denied")
    assert r.status_code == 401


def test_callback_creates_user_and_session(client, session):
    r = _callback(client, {"preferred_username": "new_student", "name": "New Student", "email": "new@centralelille.fr"})
    assert r.status_code == 302
    assert "session_id" in r.cookies

    client.cookies = {"session_id": r.cookies["session_id"]}
    data = client.get("/api/users/me").json()
    assert data["username"] == "new_student"
    assert data["email"] == "new@centralelille.fr"


def test_callback_updates_existing_user(client, session):
    existing = make_user(session, AccessLevel.USER, 99)
    r = _callback(
        client, {"preferred_username": existing.username, "name": "Updated Name", "email": "u@centralelille.fr"}
    )
    assert r.status_code == 302

    client.cookies = {"session_id": r.cookies["session_id"]}
    data = client.get("/api/users/me").json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "u@centralelille.fr"


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


def test_logout_clears_local_session(client, session):
    user = make_user(session, AccessLevel.USER, 4)
    token = make_token(session, user)

    client.cookies = {"session_id": token}
    r = client.post("/api/auth/logout")
    assert r.status_code == 200
    assert r.json()["logout_url"].startswith(METADATA["end_session_endpoint"])

    client.cookies = {"session_id": token}
    assert client.get("/api/users/me").status_code == 401


def test_logout_url_uses_client_id(client, session):
    r = _callback(client, {"preferred_username": "bob", "name": "Bob", "email": "bob@centralelille.fr"})
    client.cookies = {"session_id": r.cookies["session_id"]}

    url = client.post("/api/auth/logout").json()["logout_url"]
    assert url.startswith(METADATA["end_session_endpoint"])
    q = parse_qs(urlparse(url).query)
    assert q["client_id"] == ["matos-clap"]
    assert "id_token_hint" not in q
    assert q["post_logout_redirect_uri"] == ["https://matos.le-clap.fr/"]


def test_logout_without_session_is_graceful(client):
    r = client.post("/api/auth/logout")
    assert r.status_code == 200
    assert r.json() == {"logout_url": None}


def test_permission_denied_is_logged(client, session, caplog):
    user = make_user(session, AccessLevel.USER, 5)
    token = make_token(session, user)

    with caplog.at_level(logging.WARNING):
        r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 403
    assert "auth.permission_denied" in caplog.text
