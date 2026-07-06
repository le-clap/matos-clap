"""Tests for catalog CRUD and availability endpoints."""

from models.enums import AccessLevel, Availability
from tests.conftest import auth, dt, iso


def test_get_catalogs_requires_auth(client):
    r = client.get("/api/catalogs")
    assert r.status_code == 401


def test_get_catalogs(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category()
    f_catalog(cat, "Sony A7III")
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get("/api/catalogs", headers=auth(token))
    assert r.status_code == 200
    assert any(c["name"] == "Sony A7III" for c in r.json())


def test_create_catalog_requires_manager(client, session, f_user, f_token, f_category):
    cat = f_category()
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    r = client.post("/api/catalogs", json={"name": "X", "category_id": cat.id}, headers=auth(token))
    assert r.status_code == 403


def test_create_catalog(client, session, f_user, f_token, f_category):
    cat = f_category("Cameras")
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.post(
        "/api/catalogs",
        json={"name": "Canon R5", "category_id": cat.id, "description": "Full frame"},
        headers=auth(token),
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Canon R5"
    assert data["category"]["id"] == cat.id


def test_create_catalog_missing_category_returns_404(client, session, f_user, f_token):
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.post("/api/catalogs", json={"name": "X", "category_id": 99999}, headers=auth(token))
    assert r.status_code == 404


def test_update_catalog(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category()
    catalog = f_catalog(cat, "OldName")
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.patch(f"/api/catalogs/{catalog.id}", json={"name": "NewName"}, headers=auth(token))
    assert r.status_code == 200
    assert r.json()["name"] == "NewName"


def test_delete_catalog_with_items_returns_409(client, session, f_user, f_token, f_category, f_catalog, f_item):
    cat = f_category()
    catalog = f_catalog(cat)
    f_item(catalog)  # item references catalog
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.delete(f"/api/catalogs/{catalog.id}", headers=auth(token))
    assert r.status_code == 409


def test_available_items_requires_auth(client, session, f_category, f_catalog):
    cat = f_category()
    catalog = f_catalog(cat)

    r = client.get(
        f"/api/catalogs/{catalog.id}/available-items",
        params={"start_date": iso(0), "end_date": iso(7)},
    )
    assert r.status_code == 401


def test_available_items_naive_datetime_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category()
    catalog = f_catalog(cat)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(
        f"/api/catalogs/{catalog.id}/available-items",
        params={"start_date": "2024-01-01T00:00:00", "end_date": "2024-01-08T00:00:00"},
        headers=auth(token),
    )
    assert r.status_code == 422


def test_available_items_bad_date_range_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category()
    catalog = f_catalog(cat)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(
        f"/api/catalogs/{catalog.id}/available-items",
        params={"start_date": iso(7), "end_date": iso(0)},  # end before start
        headers=auth(token),
    )
    assert r.status_code == 422


def test_available_items_splits_available_and_unavailable(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    cat = f_category()
    catalog = f_catalog(cat)
    available_item = f_item(catalog, availability=Availability.AVAILABLE)
    maintenance_item = f_item(catalog, availability=Availability.MAINTENANCE)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(
        f"/api/catalogs/{catalog.id}/available-items",
        params={"start_date": iso(0), "end_date": iso(7)},
        headers=auth(token),
    )
    assert r.status_code == 200
    data = r.json()
    available_ids = {i["id"] for i in data["available"]}
    unavailable_ids = {i["id"] for i in data["unavailable"]}
    assert available_item.id in available_ids
    assert maintenance_item.id in unavailable_ids


def test_available_items_busy_item_moves_to_unavailable(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    cat = f_category()
    catalog = f_catalog(cat)
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(f_user(AccessLevel.USER))

    # Create a loan that overlaps [now, now+7]
    f_loan(borrower, clap, [item], start=dt(1), end=dt(5))

    r = client.get(
        f"/api/catalogs/{catalog.id}/available-items",
        params={"start_date": iso(0), "end_date": iso(7)},
        headers=auth(token),
    )
    assert r.status_code == 200
    unavailable_ids = {i["id"] for i in r.json()["unavailable"]}
    assert item.id in unavailable_ids


# ── Image upload ────────────────────────────────────────────────────────────


def test_upload_catalog_image(client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    r = client.post(
        f"/api/catalogs/{catalog.id}/image",
        files={"file": ("photo.png", b"\x89PNG\r\n\x1a\nfake-bytes", "image/png")},
        headers=auth(token),
    )
    assert r.status_code == 200
    assert r.json()["image_path"].startswith("/media/catalogs/")
    assert list((tmp_path / "catalogs").iterdir())


def test_upload_catalog_image_rejects_non_image(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    r = client.post(
        f"/api/catalogs/{catalog.id}/image",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=auth(token),
    )
    assert r.status_code == 422


def test_upload_catalog_image_requires_manager(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.CLAP))

    r = client.post(
        f"/api/catalogs/{catalog.id}/image",
        files={"file": ("photo.png", b"x", "image/png")},
        headers=auth(token),
    )
    assert r.status_code == 403
