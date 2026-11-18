"""PATCH bodies follow JSON Merge Patch: null on a NOT NULL column is rejected, null on a nullable one clears it."""

import pytest

from models.enums import AccessLevel
from tests.conftest import auth


@pytest.mark.parametrize(
    ("url", "field"),
    [
        ("/api/users/1", "access_level"),
        ("/api/categories/1", "name"),
        ("/api/catalogs/1", "category_id"),
        ("/api/items/1", "deposit_cents"),
        ("/api/requests/1", "start_date"),
        ("/api/loans/1", "total_deposit_cents"),
        ("/api/loans/1", "item_ids"),
        ("/api/loans/1/items/1/return-condition", "return_condition"),
    ],
)
def test_patch_null_on_not_null_column_is_rejected(client, f_user, f_token, url, field):
    headers = auth(f_token(f_user(AccessLevel.ADMIN)))
    r = client.patch(url, json={field: None}, headers=headers)
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", field]


def test_patch_null_on_nullable_column_clears_it(client, f_user, f_token, f_category):
    category = f_category()
    headers = auth(f_token(f_user(AccessLevel.ADMIN)))
    client.patch(f"/api/categories/{category.id}", json={"description": "x"}, headers=headers)
    r = client.patch(f"/api/categories/{category.id}", json={"description": None}, headers=headers)
    assert r.status_code == 200 and r.json()["description"] is None
