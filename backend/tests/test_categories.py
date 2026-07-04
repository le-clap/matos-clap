"""Tests for category CRUD endpoints."""

from models.enums import AccessLevel
from tests.conftest import auth, make_token, make_user


def test_get_categories_requires_auth(client):
    r = client.get("/api/categories")
    assert r.status_code == 401


def test_get_categories_as_user(client, session):
    user = make_user(session, AccessLevel.USER, 0)
    token = make_token(session, user)

    r = client.get("/api/categories", headers=auth(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_category_requires_manager(client, session):
    clap = make_user(session, AccessLevel.CLAP, 1)
    token = make_token(session, clap)

    r = client.post("/api/categories", json={"name": "Test Cat"}, headers=auth(token))
    assert r.status_code == 403


def test_create_category(client, session):
    manager = make_user(session, AccessLevel.MANAGER, 2)
    token = make_token(session, manager)

    r = client.post("/api/categories", json={"name": "Camera", "description": "Cameras"}, headers=auth(token))
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Camera"
    assert data["description"] == "Cameras"
    assert "id" in data


def test_get_category_by_id(client, session, f_user, f_token, f_category):
    cat = f_category("Audio")
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(f"/api/categories/{cat.id}", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["name"] == "Audio"


def test_get_category_not_found(client, session, f_user, f_token):
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get("/api/categories/99999", headers=auth(token))
    assert r.status_code == 404


def test_update_category(client, session, f_user, f_token, f_category):
    cat = f_category("Old Name")
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.patch(f"/api/categories/{cat.id}", json={"name": "New Name"}, headers=auth(token))
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


def test_delete_category(client, session, f_user, f_token, f_category):
    cat = f_category("ToDelete")
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.delete(f"/api/categories/{cat.id}", headers=auth(token))
    assert r.status_code == 204

    r2 = client.get(f"/api/categories/{cat.id}", headers=auth(token))
    assert r2.status_code == 404


def test_delete_category_with_catalogs_returns_409(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category("InUse")
    f_catalog(cat)  # create a catalog that references this category
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.delete(f"/api/categories/{cat.id}", headers=auth(token))
    assert r.status_code == 409
