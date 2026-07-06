"""Tests for item CRUD endpoints."""

from models.enums import AccessLevel, Availability, Condition
from tests.conftest import auth, dt


def test_get_items_requires_auth(client):
    r = client.get("/api/items")
    assert r.status_code == 401


def test_get_items(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get("/api/items", headers=auth(token))
    assert r.status_code == 200
    ids = [i["id"] for i in r.json()]
    assert item.id in ids


def test_get_items_filter_by_availability(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    avail = f_item(catalog, availability=Availability.AVAILABLE)
    maint = f_item(catalog, availability=Availability.MAINTENANCE)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get("/api/items", params={"availability": "available"}, headers=auth(token))
    assert r.status_code == 200
    ids = [i["id"] for i in r.json()]
    assert avail.id in ids
    assert maint.id not in ids


def test_get_item_by_id(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(f"/api/items/{item.id}", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["id"] == item.id


def test_get_item_not_found(client, session, f_user, f_token):
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get("/api/items/99999", headers=auth(token))
    assert r.status_code == 404


def test_create_item_requires_manager(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    r = client.post(
        "/api/items",
        json={"name": "X", "catalog_id": catalog.id, "condition": "good"},
        headers=auth(token),
    )
    assert r.status_code == 403


def test_create_item(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.post(
        "/api/items",
        json={"name": "Rode NTG5", "catalog_id": catalog.id, "condition": "new", "deposit_cents": 5000},
        headers=auth(token),
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Rode NTG5"
    assert data["deposit_cents"] == 5000
    assert data["condition"] == "new"


def test_update_item(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog, condition=Condition.GOOD)
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.patch(f"/api/items/{item.id}", json={"condition": "degraded"}, headers=auth(token))
    assert r.status_code == 200
    assert r.json()["condition"] == "degraded"


def test_soft_delete_item(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    r = client.delete(f"/api/items/{item.id}", headers=auth(token))
    assert r.status_code == 204


def test_soft_deleted_item_excluded_from_list(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    manager = f_user(AccessLevel.MANAGER)
    token = f_token(manager)

    client.delete(f"/api/items/{item.id}", headers=auth(token))

    r = client.get("/api/items", headers=auth(token))
    ids = [i["id"] for i in r.json()]
    assert item.id not in ids


# ── Item history ──────────────────────────────────────────────────────────


def test_get_item_history_requires_clap(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    token = f_token(f_user(AccessLevel.USER))

    r = client.get(f"/api/items/{item.id}/history", headers=auth(token))
    assert r.status_code == 403


def test_get_item_history_not_found(client, session, f_user, f_token):
    token = f_token(f_user(AccessLevel.CLAP))
    r = client.get("/api/items/99999/history", headers=auth(token))
    assert r.status_code == 404


def test_get_item_history_lists_stints(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower_a = f_user(AccessLevel.USER)
    borrower_b = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)

    # An older, returned stint and a current scheduled one.
    f_loan(
        borrower_a,
        clap,
        [item],
        start=dt(-10),
        end=dt(-3),
        actual_start=dt(-10),
        actual_return=dt(-4),
    )
    f_loan(borrower_b, clap, [item], start=dt(1), end=dt(5))

    r = client.get(f"/api/items/{item.id}/history", headers=auth(f_token(clap)))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    # Most recent (by effective start) first → the scheduled future loan.
    assert data[0]["borrower"]["id"] == borrower_b.id
    assert data[0]["status"] == "scheduled"
    assert data[1]["borrower"]["id"] == borrower_a.id
    assert data[1]["status"] == "returned"
    assert data[1]["actual_return_date"] is not None
