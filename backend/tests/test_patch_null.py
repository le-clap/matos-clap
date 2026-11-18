"""PATCH bodies follow JSON Merge Patch: null on a NOT NULL column is rejected, null on a nullable one clears it."""

import re

import pytest
from sqlmodel import SQLModel

from main import app
from models.enums import AccessLevel
from tests.conftest import auth


def _not_null_columns() -> set[str]:
    """Column names that are NOT NULL in every table that has them."""
    columns = [c for table in SQLModel.metadata.tables.values() for c in table.columns]
    return {c.name for c in columns} - {c.name for c in columns if c.nullable}


def _patch_cases() -> list[tuple[str, str]]:
    """Every (PATCH url, field) whose null must be rejected, discovered from the OpenAPI schema.

    A field qualifies if it maps to a NOT NULL column (catches a forgotten NonNull),
    or if its schema doesn't allow null (checks the runtime matches the contract).
    """
    spec = app.openapi()
    components = spec["components"]["schemas"]
    not_null = _not_null_columns()
    cases = []
    for path, operations in spec["paths"].items():
        if "patch" not in operations:
            continue
        ref = operations["patch"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        properties = components[ref.rsplit("/", 1)[-1]]["properties"]
        url = re.sub(r"\{\w+}", "1", path)  # body validation runs before any lookup
        for field, schema in properties.items():
            allows_null = any(option.get("type") == "null" for option in schema.get("anyOf", []))
            if field in not_null or not allows_null:
                cases.append((url, field))
    return cases


@pytest.mark.parametrize(("url", "field"), _patch_cases())
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
