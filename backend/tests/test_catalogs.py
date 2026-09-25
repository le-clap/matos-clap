"""Tests for catalog CRUD and availability endpoints."""

from models.enums import AccessLevel, Availability, RequestStatus
from models.models import Catalog, Request, RequestedCatalog
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


def test_delete_empty_catalog_purges(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.delete(f"/api/catalogs/{catalog.id}", headers=auth(token))
    assert r.status_code == 204
    assert session.get(Catalog, catalog.id) is None


def test_delete_catalog_with_only_archived_items_archives(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    """Regression test: a reference whose items were all archived must not be stuck forever."""
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    clap = f_user(AccessLevel.CLAP)
    borrower = f_user(AccessLevel.USER)
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    f_loan(borrower, clap, [item], actual_start=dt(-5), actual_return=dt(-1))
    r = client.delete(f"/api/items/{item.id}", headers=auth(token))
    assert r.status_code == 204  # item archived, not purged, since it has history

    r = client.delete(f"/api/catalogs/{catalog.id}", headers=auth(token))
    assert r.status_code == 204

    archived = session.get(Catalog, catalog.id)
    assert archived is not None
    assert archived.deleted_at is not None


def test_delete_catalog_referenced_by_request_archives(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    manager = f_user(AccessLevel.MANAGER)
    borrower = f_user(AccessLevel.USER)
    token = f_token(manager)

    request = Request(
        borrower_id=borrower.id,
        phone_number="0600000000",
        start_date=dt(1),
        end_date=dt(5),
        status=RequestStatus.PENDING,
    )
    session.add(request)
    session.flush()
    session.add(RequestedCatalog(request_id=request.id, catalog_id=catalog.id, quantity=1))
    session.commit()

    r = client.delete(f"/api/catalogs/{catalog.id}", headers=auth(token))
    assert r.status_code == 204

    archived = session.get(Catalog, catalog.id)
    assert archived is not None
    assert archived.deleted_at is not None


def test_update_archived_catalog_returns_404(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    catalog.deleted_at = dt(-1)
    session.add(catalog)
    session.commit()
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.patch(f"/api/catalogs/{catalog.id}", json={"name": "NewName"}, headers=auth(token))
    assert r.status_code == 404


def test_get_catalogs_excludes_archived(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    catalog.deleted_at = dt(-1)
    session.add(catalog)
    session.commit()
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get("/api/catalogs", headers=auth(token))
    assert r.status_code == 200
    ids = [c["id"] for c in r.json()]
    assert catalog.id not in ids


def test_available_items_for_archived_catalog_returns_404(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    catalog.deleted_at = dt(-1)
    session.add(catalog)
    session.commit()
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(
        f"/api/catalogs/{catalog.id}/available-items",
        params={"start_date": iso(0), "end_date": iso(7)},
        headers=auth(token),
    )
    assert r.status_code == 404


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


# ── Image gallery ───────────────────────────────────────────────────────────


def _upload_image(client, token, catalog_id, filename="photo.png"):
    return client.post(
        f"/api/catalogs/{catalog_id}/images",
        files={"file": (filename, b"\x89PNG\r\n\x1a\nfake-bytes", "image/png")},
        headers=auth(token),
    )


def test_upload_catalog_image(client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    r = _upload_image(client, token, catalog.id)
    assert r.status_code == 201
    data = r.json()
    assert data["image_path"].startswith("/media/catalogs/")
    assert data["position"] == 0
    assert list((tmp_path / "catalogs").iterdir())


def test_upload_catalog_image_appends(client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    first = _upload_image(client, token, catalog.id, "one.png").json()
    second = _upload_image(client, token, catalog.id, "two.png").json()
    assert [first["position"], second["position"]] == [0, 1]

    catalog_data = client.get(f"/api/catalogs/{catalog.id}", headers=auth(token)).json()
    assert [img["position"] for img in catalog_data["images"]] == [0, 1]
    assert catalog_data["image_path"] == first["image_path"]


def test_upload_catalog_image_after_delete_avoids_position_collision(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    images = [_upload_image(client, token, catalog.id, f"{n}.png").json() for n in range(3)]
    middle = images[1]

    r = client.delete(f"/api/catalogs/{catalog.id}/images/{middle['id']}", headers=auth(token))
    assert r.status_code == 204

    _upload_image(client, token, catalog.id, "fourth.png")
    catalog_data = client.get(f"/api/catalogs/{catalog.id}", headers=auth(token)).json()
    positions = [img["position"] for img in catalog_data["images"]]
    assert len(positions) == len(set(positions))  # no two images share a position


def test_upload_catalog_image_rejects_non_image(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    r = client.post(
        f"/api/catalogs/{catalog.id}/images",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=auth(token),
    )
    assert r.status_code == 422


def test_upload_catalog_image_requires_manager(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.CLAP))

    r = client.post(
        f"/api/catalogs/{catalog.id}/images",
        files={"file": ("photo.png", b"x", "image/png")},
        headers=auth(token),
    )
    assert r.status_code == 403


def test_delete_catalog_image(client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    image = _upload_image(client, token, catalog.id).json()
    assert list((tmp_path / "catalogs").iterdir())

    r = client.delete(f"/api/catalogs/{catalog.id}/images/{image['id']}", headers=auth(token))
    assert r.status_code == 204
    assert not list((tmp_path / "catalogs").iterdir())

    updated = client.get(f"/api/catalogs/{catalog.id}", headers=auth(token)).json()
    assert updated["images"] == []
    assert updated["image_path"] is None


def test_delete_catalog_image_wrong_catalog_returns_404(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog_a = f_catalog(cat, "A")
    catalog_b = f_catalog(cat, "B")
    token = f_token(f_user(AccessLevel.MANAGER))

    image = _upload_image(client, token, catalog_a.id).json()

    r = client.delete(f"/api/catalogs/{catalog_b.id}/images/{image['id']}", headers=auth(token))
    assert r.status_code == 404


def test_delete_catalog_image_requires_manager(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    manager_token = f_token(f_user(AccessLevel.MANAGER))
    clap_token = f_token(f_user(AccessLevel.CLAP))

    image = _upload_image(client, manager_token, catalog.id).json()

    r = client.delete(f"/api/catalogs/{catalog.id}/images/{image['id']}", headers=auth(clap_token))
    assert r.status_code == 403


def test_reorder_catalog_images(client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    first = _upload_image(client, token, catalog.id, "one.png").json()
    second = _upload_image(client, token, catalog.id, "two.png").json()
    reversed_ids = [second["id"], first["id"]]

    r = client.put(
        f"/api/catalogs/{catalog.id}/images/order",
        json={"image_ids": reversed_ids},
        headers=auth(token),
    )
    assert r.status_code == 200
    data = r.json()
    assert [img["id"] for img in data["images"]] == reversed_ids
    assert data["image_path"] == data["images"][0]["image_path"]


def test_reorder_catalog_images_rejects_mismatched_ids(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    _upload_image(client, token, catalog.id)

    r = client.put(
        f"/api/catalogs/{catalog.id}/images/order",
        json={"image_ids": [999999]},
        headers=auth(token),
    )
    assert r.status_code == 422


def test_delete_catalog_purges_all_image_files(
    client, session, f_user, f_token, f_category, f_catalog, tmp_path, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    cat = f_category()
    catalog = f_catalog(cat)
    token = f_token(f_user(AccessLevel.MANAGER))

    _upload_image(client, token, catalog.id, "one.png")
    _upload_image(client, token, catalog.id, "two.png")
    assert len(list((tmp_path / "catalogs").iterdir())) == 2

    r = client.delete(f"/api/catalogs/{catalog.id}", headers=auth(token))
    assert r.status_code == 204
    assert not list((tmp_path / "catalogs").iterdir())
