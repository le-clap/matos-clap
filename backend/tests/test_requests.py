"""Tests for request management and recommendations endpoints."""

from models.enums import AccessLevel, Availability
from tests.conftest import auth, iso


def _request_body(borrower_id: int, catalog_id: int, *, quantity: int = 1) -> dict:
    return {
        "borrower_id": borrower_id,
        "phone_number": "0612345678",
        "start_date": iso(3),
        "end_date": iso(10),
        "requested_catalogs": [{"catalog_id": catalog_id, "quantity": quantity}],
    }


def test_create_request(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token))
    assert r.status_code == 201
    data = r.json()
    assert data["borrower"]["id"] == user.id
    assert data["status"] == "pending"
    assert len(data["requested_catalogs"]) == 1


def test_create_request_for_other_user_is_forbidden(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    other = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.post("/api/requests", json=_request_body(other.id, catalog.id), headers=auth(token))
    assert r.status_code == 403


def test_create_request_missing_catalog_returns_404(client, session, f_user, f_token):
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.post("/api/requests", json=_request_body(user.id, 99999), headers=auth(token))
    assert r.status_code == 404


def test_create_request_naive_datetime_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    body = {
        "borrower_id": user.id,
        "phone_number": "0612345678",
        "start_date": "2024-01-01T00:00:00",  # naive
        "end_date": "2024-01-08T00:00:00",
        "requested_catalogs": [{"catalog_id": catalog.id, "quantity": 1}],
    }
    r = client.post("/api/requests", json=body, headers=auth(token))
    assert r.status_code == 422


def test_get_requests_user_sees_only_own(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())

    # user_a creates a request
    user_a = f_user(AccessLevel.USER)
    token_a = f_token(user_a)
    r_a = client.post("/api/requests", json=_request_body(user_a.id, catalog.id), headers=auth(token_a))
    assert r_a.status_code == 201

    # user_b creates a request
    user_b = f_user(AccessLevel.USER)
    r_b = client.post("/api/requests", json=_request_body(user_b.id, catalog.id), headers=auth(f_token(user_b)))
    assert r_b.status_code == 201

    # We test from user_a's perspective
    r = client.get("/api/requests", headers=auth(token_a))
    assert r.status_code == 200

    borrower_ids = {req["borrower"]["id"] for req in r.json()["items"]}
    assert borrower_ids == {user_a.id}


def test_get_requests_clap_sees_all(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user_a = f_user(AccessLevel.USER)
    user_b = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token_a = f_token(user_a)
    token_b = f_token(user_b)
    token_clap = f_token(clap)

    client.post("/api/requests", json=_request_body(user_a.id, catalog.id), headers=auth(token_a))
    client.post("/api/requests", json=_request_body(user_b.id, catalog.id), headers=auth(token_b))

    r = client.get("/api/requests", headers=auth(token_clap))
    assert r.status_code == 200
    borrower_ids = {req["borrower"]["id"] for req in r.json()["items"]}
    assert user_a.id in borrower_ids
    assert user_b.id in borrower_ids


def test_get_request_by_id_requires_clap(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    create_r = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token))
    req_id = create_r.json()["id"]

    r = client.get(f"/api/requests/{req_id}", headers=auth(token))
    assert r.status_code == 403


def test_get_recommendations_requires_clap(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    create_r = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token))
    req_id = create_r.json()["id"]

    r = client.get(f"/api/requests/{req_id}/recommendations", headers=auth(token))
    assert r.status_code == 403


def test_get_recommendations_returns_available_items(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog, availability=Availability.AVAILABLE)
    user = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token_user = f_token(user)
    token_clap = f_token(clap)

    create_r = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token_user))
    req_id = create_r.json()["id"]

    r = client.get(f"/api/requests/{req_id}/recommendations", headers=auth(token_clap))
    assert r.status_code == 200
    data = r.json()
    assert len(data["recommendations"]) == 1
    rec = data["recommendations"][0]
    assert item.id in rec["recommended_item_ids"]


def test_get_recommendations_warns_if_insufficient_stock(
    client, session, f_user, f_token, f_category, f_catalog, f_item
):
    """Requesting qty=2 when only 1 item exists should warn."""
    catalog = f_catalog(f_category())
    f_item(catalog, availability=Availability.AVAILABLE)
    user = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token_user = f_token(user)
    token_clap = f_token(clap)

    body = _request_body(user.id, catalog.id, quantity=2)
    create_r = client.post("/api/requests", json=body, headers=auth(token_user))
    req_id = create_r.json()["id"]

    r = client.get(f"/api/requests/{req_id}/recommendations", headers=auth(token_clap))
    assert r.status_code == 200
    rec = r.json()["recommendations"][0]
    assert len(rec["warnings"]) > 0


def test_update_request_requires_clap(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    create_r = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token))
    req_id = create_r.json()["id"]

    r = client.patch(f"/api/requests/{req_id}", json={"status": "approved"}, headers=auth(token))
    assert r.status_code == 403


def test_delete_request_requires_clap(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token_user = f_token(user)
    token_clap = f_token(clap)

    create_r = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token_user))
    req_id = create_r.json()["id"]

    r = client.delete(f"/api/requests/{req_id}", headers=auth(token_clap))
    assert r.status_code == 204


# ── Owner edit / delete of pending requests ─────────────────────────────────


def test_owner_can_edit_pending_request(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    req_id = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token)).json()["id"]

    r = client.patch(
        f"/api/requests/{req_id}",
        json={"reason": "Mise à jour", "phone_number": "0707070707"},
        headers=auth(token),
    )
    assert r.status_code == 200
    assert r.json()["reason"] == "Mise à jour"
    assert r.json()["phone_number"] == "+33707070707"


def test_owner_cannot_edit_other_users_request(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    owner = f_user(AccessLevel.USER)
    other = f_user(AccessLevel.USER)
    req_id = client.post(
        "/api/requests", json=_request_body(owner.id, catalog.id), headers=auth(f_token(owner))
    ).json()["id"]

    r = client.patch(f"/api/requests/{req_id}", json={"reason": "x"}, headers=auth(f_token(other)))
    assert r.status_code == 403


def test_owner_can_delete_pending_request(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)
    req_id = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token)).json()["id"]

    r = client.delete(f"/api/requests/{req_id}", headers=auth(token))
    assert r.status_code == 204


# ── Refuse / reopen ─────────────────────────────────────────────────────────


def test_refuse_and_reopen_request(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    req_id = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(f_token(user))).json()[
        "id"
    ]
    token_clap = f_token(clap)

    refused = client.patch(f"/api/requests/{req_id}", json={"status": "refused"}, headers=auth(token_clap))
    assert refused.status_code == 200

    reopened = client.patch(f"/api/requests/{req_id}", json={"status": "pending"}, headers=auth(token_clap))
    assert reopened.status_code == 200


# ── Phone number validation ─────────────────────────────────────────────────


def test_create_request_invalid_phone_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    body = _request_body(user.id, catalog.id)
    body["phone_number"] = "12345"
    r = client.post("/api/requests", json=body, headers=auth(token))
    assert r.status_code == 422


def test_create_request_normalizes_phone(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    body = _request_body(user.id, catalog.id)
    body["phone_number"] = "06 12 34 56 78"
    r = client.post("/api/requests", json=body, headers=auth(token))
    assert r.status_code == 201
    assert r.json()["phone_number"] == "+33612345678"


# ── Patch date integrity ────────────────────────────────────────────────────


def test_patch_request_end_before_start_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    catalog = f_catalog(f_category())
    user = f_user(AccessLevel.USER)
    token = f_token(user)
    # _request_body uses iso(3) → iso(10).
    req_id = client.post("/api/requests", json=_request_body(user.id, catalog.id), headers=auth(token)).json()["id"]

    # Patching only the end date to before the existing start date is rejected.
    r = client.patch(f"/api/requests/{req_id}", json={"end_date": iso(1)}, headers=auth(token))
    assert r.status_code == 422
