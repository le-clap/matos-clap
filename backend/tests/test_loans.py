"""Tests for loan lifecycle endpoints."""

from datetime import UTC, datetime, timedelta

from models.enums import AccessLevel
from models.models import Item
from tests.conftest import auth, dt, iso

# ── Helpers ───────────────────────────────────────────────────────────────────


def _loan_body(borrower_id: int, item_ids: list[int], **kwargs) -> dict:
    base = {
        "borrower_id": borrower_id,
        "start_date": iso(1),
        "end_date": iso(8),
        "item_ids": item_ids,
        "total_deposit_cents": 0,
    }
    base.update(kwargs)
    return base


# ── Creation ──────────────────────────────────────────────────────────────────


def test_create_loan_requires_clap(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.post("/api/loans", json=_loan_body(user.id, [item.id]), headers=auth(token))
    assert r.status_code == 403


def test_create_loan(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    r = client.post("/api/loans", json=_loan_body(borrower.id, [item.id]), headers=auth(token))
    assert r.status_code == 201
    data = r.json()
    assert data["loan"]["borrower"]["id"] == borrower.id
    assert len(data["loan"]["loaned_items"]) == 1
    assert data["warnings"] == []


def test_create_loan_warns_on_date_conflict(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    # Pre-existing loan overlaps the new one
    f_loan(borrower, clap, [item], start=dt(2), end=dt(9))

    r = client.post("/api/loans", json=_loan_body(borrower.id, [item.id]), headers=auth(token))
    assert r.status_code == 201
    assert any(w["code"] == "ITEM_DATE_CONFLICT" for w in r.json()["warnings"])


def test_create_loan_fails_on_duplicate_item_ids(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    r = client.post("/api/loans", json=_loan_body(borrower.id, [item.id, item.id]), headers=auth(token))
    assert r.status_code == 422


def test_create_loan_fails_on_archived_item(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    manager = f_user(AccessLevel.MANAGER)
    clap = f_user(AccessLevel.CLAP)
    borrower = f_user(AccessLevel.USER)
    m_token = f_token(manager)
    c_token = f_token(clap)

    # The item needs loan history, otherwise deleting it purges the row outright.
    f_loan(borrower, clap, [item], actual_start=dt(-2), actual_return=dt(-1))
    client.delete(f"/api/items/{item.id}", headers=auth(m_token))

    r = client.post("/api/loans", json=_loan_body(borrower.id, [item.id]), headers=auth(c_token))
    assert r.status_code == 422


def test_create_loan_fails_on_purged_item(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    manager = f_user(AccessLevel.MANAGER)
    clap = f_user(AccessLevel.CLAP)
    borrower = f_user(AccessLevel.USER)
    m_token = f_token(manager)
    c_token = f_token(clap)

    # No loan history: deleting purges the row outright.
    r = client.delete(f"/api/items/{item.id}", headers=auth(m_token))
    assert r.status_code == 204
    assert session.get(Item, item.id) is None

    r = client.post("/api/loans", json=_loan_body(borrower.id, [item.id]), headers=auth(c_token))
    assert r.status_code == 404


def test_create_loan_naive_datetime_returns_422(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    body = {
        "borrower_id": borrower.id,
        "start_date": "2024-01-01T00:00:00",  # naive
        "end_date": "2024-01-08T00:00:00",
        "item_ids": [item.id],
    }
    r = client.post("/api/loans", json=body, headers=auth(token))
    assert r.status_code == 422


def test_create_loan_marks_request_approved(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    b_token = f_token(borrower)
    c_token = f_token(clap)

    # Create a request first
    req_body = {
        "borrower_id": borrower.id,
        "phone_number": "0600000000",
        "start_date": iso(1),
        "end_date": iso(8),
        "requested_catalogs": [{"catalog_id": catalog.id, "quantity": 1}],
    }
    req_r = client.post("/api/requests", json=req_body, headers=auth(b_token))
    req_id = req_r.json()["id"]

    # Create loan from that request
    body = _loan_body(borrower.id, [item.id], request_id=req_id)
    client.post("/api/loans", json=body, headers=auth(c_token))

    # Verify request is now approved
    r = client.get(f"/api/requests/{req_id}", headers=auth(c_token))
    assert r.json()["status"] == "approved"


# ── Listing / filtering ───────────────────────────────────────────────────────


def test_get_loans_user_sees_only_own(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item_a = f_item(catalog)
    item_b = f_item(catalog)
    borrower_a = f_user(AccessLevel.USER)
    borrower_b = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    f_loan(borrower_a, clap, [item_a])
    f_loan(borrower_b, clap, [item_b])

    token_a = f_token(borrower_a)
    r = client.get("/api/loans", headers=auth(token_a))
    assert r.status_code == 200
    for loan in r.json()["items"]:
        assert loan["borrower"]["id"] == borrower_a.id


def test_get_loans_filters_loans_by_status(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan_scheduled = f_loan(borrower, clap, [f_item(catalog)])
    loan_active = f_loan(borrower, clap, [f_item(catalog)], actual_start=now - timedelta(hours=1))
    loan_returned = f_loan(
        borrower, clap, [f_item(catalog)], actual_start=now - timedelta(days=2), actual_return=now - timedelta(hours=1)
    )

    for status, expected_count, loan in [
        ("scheduled", 1, loan_scheduled),
        ("active", 1, loan_active),
        ("returned", 1, loan_returned),
    ]:
        r = client.get(f"/api/loans?status={status}", headers=auth(token))
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == expected_count
        assert data["items"][0]["id"] == loan.id


def test_get_loans_no_filter_returns_all(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    for item in [f_item(catalog), f_item(catalog), f_item(catalog)]:
        f_loan(borrower, clap, [item])

    r = client.get("/api/loans", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["total"] == 3


def test_get_loans_search_filters_by_borrower_name(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    catalog = f_catalog(f_category())
    item_a = f_item(catalog)
    item_b = f_item(catalog)
    borrower_a = f_user(AccessLevel.USER)
    borrower_b = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    f_loan(borrower_a, clap, [item_a])
    f_loan(borrower_b, clap, [item_b])

    params = {"search": "user 0"}
    r = client.get("/api/loans", params=params, headers=auth(token))
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["search"] == params["search"]
    assert all(loan["borrower"]["id"] == borrower_a.id for loan in data["items"])


# ── Return ────────────────────────────────────────────────────────────────────


def test_return_loan(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item], actual_start=now - timedelta(hours=2))

    r = client.post(
        f"/api/loans/{loan.id}/return",
        json={"retained_deposit_cents": 0},
        headers=auth(token),
    )
    assert r.status_code == 200
    data = r.json()
    assert data["actual_return_date"] is not None
    assert data["retained_deposit_cents"] == 0


def test_return_loan_updates_deposit(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog, deposit_cents=10000)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item], actual_start=now - timedelta(hours=2), total_deposit_cents=10000)

    r = client.post(
        f"/api/loans/{loan.id}/return",
        json={"retained_deposit_cents": 5000},
        headers=auth(token),
    )
    assert r.status_code == 200
    assert r.json()["retained_deposit_cents"] == 5000


def test_return_loan_retained_exceeds_total_returns_422(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item], actual_start=now - timedelta(hours=2), total_deposit_cents=1000)

    r = client.post(
        f"/api/loans/{loan.id}/return",
        json={"retained_deposit_cents": 9999},
        headers=auth(token),
    )
    assert r.status_code == 422


def test_return_loan_not_started_returns_409(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    loan = f_loan(borrower, clap, [item])  # no actual_start_date

    r = client.post(
        f"/api/loans/{loan.id}/return",
        json={"retained_deposit_cents": 0},
        headers=auth(token),
    )
    assert r.status_code == 409


def test_return_loan_already_returned_returns_409(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item], actual_start=now - timedelta(days=2), actual_return=now - timedelta(hours=1))

    r = client.post(
        f"/api/loans/{loan.id}/return",
        json={"retained_deposit_cents": 0},
        headers=auth(token),
    )
    assert r.status_code == 409


# ── Partial return ────────────────────────────────────────────────────────────


def test_partial_return_loan(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item_a = f_item(catalog)
    item_b = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item_a, item_b], actual_start=now - timedelta(hours=2))

    r = client.post(
        f"/api/loans/{loan.id}/partial-return",
        json={"items": [{"item_id": item_a.id, "return_condition": "good"}]},
        headers=auth(token),
    )
    assert r.status_code == 200
    loaned_items = r.json()["loaned_items"]
    returned = [li for li in loaned_items if li["item"]["id"] == item_a.id]
    still_out = [li for li in loaned_items if li["item"]["id"] == item_b.id]
    assert returned[0]["actual_return_date"] is not None
    assert still_out[0]["actual_return_date"] is None


def test_partial_return_all_items_is_rejected(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    """Partial return must leave at least one item active."""
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item], actual_start=now - timedelta(hours=2))

    r = client.post(
        f"/api/loans/{loan.id}/partial-return",
        json={"items": [{"item_id": item.id}]},
        headers=auth(token),
    )
    assert r.status_code == 422


# ── Timeline ──────────────────────────────────────────────────────────────────


def test_get_timeline_requires_clap(client, session, f_user, f_token):
    user = f_user(AccessLevel.USER)
    token = f_token(user)

    r = client.get(
        "/api/loans/timeline",
        params={"start_date": iso(0), "end_date": iso(7)},
        headers=auth(token),
    )
    assert r.status_code == 403


def test_get_timeline_naive_datetime_returns_422(client, session, f_user, f_token):
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    r = client.get(
        "/api/loans/timeline",
        params={"start_date": "2024-01-01T00:00:00", "end_date": "2024-01-08T00:00:00"},
        headers=auth(token),
    )
    assert r.status_code == 422


def test_get_timeline_returns_overlapping_loans(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    # This loan overlaps [now, now+7]
    loan = f_loan(borrower, clap, [item], start=now + timedelta(days=2), end=now + timedelta(days=5))

    r = client.get(
        "/api/loans/timeline",
        params={"start_date": iso(0), "end_date": iso(7)},
        headers=auth(token),
    )
    assert r.status_code == 200
    loan_ids = [entry["loan_id"] for entry in r.json()["loans"]]
    assert loan.id in loan_ids


# ── Patch / delete ────────────────────────────────────────────────────────────


def test_patch_loan_requires_clap(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    loan = f_loan(borrower, clap, [item])
    token = f_token(borrower)

    r = client.patch(f"/api/loans/{loan.id}", json={"comments": "test"}, headers=auth(token))
    assert r.status_code == 403


def test_patch_loan(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    loan = f_loan(borrower, clap, [item])
    token = f_token(clap)

    r = client.patch(f"/api/loans/{loan.id}", json={"comments": "updated comment"}, headers=auth(token))
    assert r.status_code == 200
    assert r.json()["comments"] == "updated comment"


def test_patch_loan_end_before_start_returns_422(
    client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    loan = f_loan(borrower, clap, [item], start=dt(2), end=dt(9))
    token = f_token(clap)

    # Patching only the end date to before the existing start date is rejected.
    r = client.patch(f"/api/loans/{loan.id}", json={"end_date": iso(1)}, headers=auth(token))
    assert r.status_code == 422


def test_delete_loan(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    loan = f_loan(borrower, clap, [item])
    token = f_token(clap)

    r = client.delete(f"/api/loans/{loan.id}", headers=auth(token))
    assert r.status_code == 204


# ── Status exposure ─────────────────────────────────────────────────────────


def test_loan_response_exposes_status(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    scheduled = f_loan(borrower, clap, [f_item(catalog)])
    active = f_loan(borrower, clap, [f_item(catalog)], actual_start=now - timedelta(hours=1))
    returned = f_loan(
        borrower,
        clap,
        [f_item(catalog)],
        actual_start=now - timedelta(days=1),
        actual_return=now - timedelta(hours=1),
    )

    expected = {scheduled.id: "scheduled", active.id: "active", returned.id: "returned"}
    for loan_id, status in expected.items():
        r = client.get(f"/api/loans/{loan_id}", headers=auth(token))
        assert r.status_code == 200
        assert r.json()["status"] == status


# ── One loan per request ────────────────────────────────────────────────────


def test_second_loan_from_same_request_returns_409(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item_a = f_item(catalog)
    item_b = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    b_token = f_token(borrower)
    c_token = f_token(clap)

    req_body = {
        "borrower_id": borrower.id,
        "phone_number": "0600000000",
        "start_date": iso(1),
        "end_date": iso(8),
        "requested_catalogs": [{"catalog_id": catalog.id, "quantity": 1}],
    }
    req_id = client.post("/api/requests", json=req_body, headers=auth(b_token)).json()["id"]

    first = client.post(
        "/api/loans", json=_loan_body(borrower.id, [item_a.id], request_id=req_id), headers=auth(c_token)
    )
    assert first.status_code == 201

    # The request now exposes the linked loan and refuses a second one.
    req = client.get(f"/api/requests/{req_id}", headers=auth(c_token)).json()
    assert req["loan_id"] == first.json()["loan"]["id"]

    second = client.post(
        "/api/loans", json=_loan_body(borrower.id, [item_b.id], request_id=req_id), headers=auth(c_token)
    )
    assert second.status_code == 409


def test_cannot_create_loan_from_refused_request(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    c_token = f_token(clap)

    req_body = {
        "borrower_id": borrower.id,
        "phone_number": "0600000000",
        "start_date": iso(1),
        "end_date": iso(8),
        "requested_catalogs": [{"catalog_id": catalog.id, "quantity": 1}],
    }
    req_id = client.post("/api/requests", json=req_body, headers=auth(f_token(borrower))).json()["id"]
    client.patch(f"/api/requests/{req_id}", json={"status": "refused"}, headers=auth(c_token))

    r = client.post("/api/loans", json=_loan_body(borrower.id, [item.id], request_id=req_id), headers=auth(c_token))
    assert r.status_code == 409


# ── Editing items while scheduled ───────────────────────────────────────────


def test_edit_scheduled_loan_items(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item_a = f_item(catalog)
    item_b = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)

    loan = f_loan(borrower, clap, [item_a])  # scheduled (no actual_start)

    r = client.patch(f"/api/loans/{loan.id}", json={"item_ids": [item_b.id]}, headers=auth(token))
    assert r.status_code == 200
    item_ids = [li["item"]["id"] for li in r.json()["loaned_items"]]
    assert item_ids == [item_b.id]


def test_cannot_edit_items_of_started_loan(client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan):
    catalog = f_catalog(f_category())
    item_a = f_item(catalog)
    item_b = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    token = f_token(clap)
    now = datetime.now(UTC)

    loan = f_loan(borrower, clap, [item_a], actual_start=now - timedelta(hours=1))

    r = client.patch(f"/api/loans/{loan.id}", json={"item_ids": [item_b.id]}, headers=auth(token))
    assert r.status_code == 409


# ── Delete sends the request back to pending ────────────────────────────────


def test_delete_loan_reopens_request(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    clap = f_user(AccessLevel.CLAP)
    c_token = f_token(clap)

    req_body = {
        "borrower_id": borrower.id,
        "phone_number": "0600000000",
        "start_date": iso(1),
        "end_date": iso(8),
        "requested_catalogs": [{"catalog_id": catalog.id, "quantity": 1}],
    }
    req_id = client.post("/api/requests", json=req_body, headers=auth(f_token(borrower))).json()["id"]
    loan_id = client.post(
        "/api/loans", json=_loan_body(borrower.id, [item.id], request_id=req_id), headers=auth(c_token)
    ).json()["loan"]["id"]

    assert client.get(f"/api/requests/{req_id}", headers=auth(c_token)).json()["status"] == "approved"

    assert client.delete(f"/api/loans/{loan_id}", headers=auth(c_token)).status_code == 204

    req = client.get(f"/api/requests/{req_id}", headers=auth(c_token)).json()
    assert req["status"] == "pending"
    assert req["loan_id"] is None
