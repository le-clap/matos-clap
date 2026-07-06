"""Tests for user management endpoints."""

from models.enums import AccessLevel
from tests.conftest import auth, make_token, make_user


def test_get_users_requires_clap(client, session):
    user = make_user(session, AccessLevel.USER, 0)
    token = make_token(session, user)

    r = client.get("/api/users", headers=auth(token))
    assert r.status_code == 403


def test_get_users_as_clap(client, session):
    clap = make_user(session, AccessLevel.CLAP, 1)
    token = make_token(session, clap)

    r = client.get("/api/users", headers=auth(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert any(u["username"] == clap.username for u in r.json())


def test_get_me(client, session):
    user = make_user(session, AccessLevel.USER, 2)
    token = make_token(session, user)

    r = client.get("/api/users/me", headers=auth(token))
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["access_level"] == "user"


def test_get_user_by_id_requires_clap(client, session):
    user = make_user(session, AccessLevel.USER, 3)
    token = make_token(session, user)

    r = client.get(f"/api/users/{user.id}", headers=auth(token))
    assert r.status_code == 403


def test_get_user_by_id_as_clap(client, session):
    target = make_user(session, AccessLevel.USER, 4)
    clap = make_user(session, AccessLevel.CLAP, 5)
    token = make_token(session, clap)

    r = client.get(f"/api/users/{target.id}", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["id"] == target.id


def test_get_user_by_id_not_found(client, session):
    clap = make_user(session, AccessLevel.CLAP, 6)
    token = make_token(session, clap)

    r = client.get("/api/users/99999", headers=auth(token))
    assert r.status_code == 404


def test_update_user_role_requires_admin(client, session):
    target = make_user(session, AccessLevel.USER, 7)
    manager = make_user(session, AccessLevel.MANAGER, 8)
    token = make_token(session, manager)

    r = client.patch(f"/api/users/{target.id}", json={"access_level": "clap"}, headers=auth(token))
    assert r.status_code == 403


def test_update_user_role_as_admin(client, session):
    target = make_user(session, AccessLevel.USER, 9)
    admin = make_user(session, AccessLevel.ADMIN, 10)
    token = make_token(session, admin)

    r = client.patch(f"/api/users/{target.id}", json={"access_level": "clap"}, headers=auth(token))
    assert r.status_code == 200
    assert r.json()["access_level"] == "clap"


def test_update_user_not_found(client, session):
    admin = make_user(session, AccessLevel.ADMIN, 11)
    token = make_token(session, admin)

    r = client.patch("/api/users/99999", json={"access_level": "clap"}, headers=auth(token))
    assert r.status_code == 404
