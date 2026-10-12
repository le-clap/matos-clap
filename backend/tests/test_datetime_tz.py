"""Timezone handling: naive input is rejected, offsets are stored as UTC, responses carry an offset."""

from datetime import UTC, datetime

import pytest
from sqlmodel import select

from models.enums import AccessLevel
from models.models import Loan
from tests.conftest import auth, dt, iso


def _loan_body(borrower_id: int, item_ids: list[int], start: str, end: str) -> dict:
    return {
        "borrower_id": borrower_id,
        "start_date": start,
        "end_date": end,
        "item_ids": item_ids,
        "total_deposit_cents": 0,
    }


def test_naive_datetime_is_rejected(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    token = f_token(f_user(AccessLevel.CLAP))

    body = _loan_body(borrower.id, [item.id], "2030-01-01T14:00:00", "2030-01-08T14:00:00")
    r = client.post("/api/loans", json=body, headers=auth(token))
    assert r.status_code == 422


def test_offset_datetime_is_stored_as_utc(client, session, f_user, f_token, f_category, f_catalog, f_item):
    catalog = f_catalog(f_category())
    item = f_item(catalog)
    borrower = f_user(AccessLevel.USER)
    token = f_token(f_user(AccessLevel.CLAP))

    body = _loan_body(borrower.id, [item.id], "2030-01-01T16:00:00+02:00", "2030-01-08T16:00:00+02:00")
    r = client.post("/api/loans", json=body, headers=auth(token))
    assert r.status_code == 201

    loan = session.exec(select(Loan).where(Loan.id == r.json()["loan"]["id"])).one()
    assert loan.start_date == datetime(2030, 1, 1, 14, 0, tzinfo=UTC)
    assert loan.start_date.utcoffset() == UTC.utcoffset(None)


def _datetime_strings(node) -> list[str]:
    """Collect every ISO datetime string anywhere in a JSON payload."""
    if isinstance(node, dict):
        return [d for v in node.values() for d in _datetime_strings(v)]
    if isinstance(node, list):
        return [d for v in node for d in _datetime_strings(v)]
    return [node] if isinstance(node, str) and node[:2] == "20" and "T" in node else []


@pytest.mark.parametrize(
    ("url", "params"),
    [
        ("/api/loans", None),
        ("/api/loans/timeline", {"start_date": iso(-10), "end_date": iso(10)}),
        ("/api/items/{item_id}/history", None),
    ],
    ids=["loans", "timeline", "item-history"],
)
def test_responses_carry_utc_offset(
    url, params, client, session, f_user, f_token, f_category, f_catalog, f_item, f_loan
):
    item = f_item(f_catalog(f_category()))
    clap = f_user(AccessLevel.CLAP)
    f_loan(f_user(AccessLevel.USER), clap, [item], start=dt(-2), end=dt(5), actual_start=dt(-2))

    r = client.get(url.format(item_id=item.id), params=params, headers=auth(f_token(clap)))
    assert r.status_code == 200
    found = _datetime_strings(r.json())
    assert found
    assert all(datetime.fromisoformat(d).utcoffset() is not None for d in found)
