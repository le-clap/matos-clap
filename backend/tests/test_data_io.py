"""Tests for CSV import / export of catalogs and items."""

from models.enums import AccessLevel
from tests.conftest import auth


def _file(text: str) -> dict:
    return {"file": ("data.csv", text.encode("utf-8"), "text/csv")}


# ──────────────────────────────── export ─────────────────────────────────


def test_export_requires_manager(client, session, f_user, f_token):
    token = f_token(f_user(AccessLevel.CLAP))
    r = client.get("/api/io/catalogs/export", headers=auth(token))
    assert r.status_code == 403


def test_export_catalogs(client, session, f_user, f_token, f_category, f_catalog):
    cat = f_category("Caméras")
    f_catalog(cat, "Sony A7")
    token = f_token(f_user(AccessLevel.MANAGER))

    r = client.get("/api/io/catalogs/export", headers=auth(token))
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    lines = r.text.splitlines()
    assert lines[0] == "id,name,description,category,image_path"
    assert any("Sony A7" in line and "Caméras" in line for line in lines[1:])


def test_export_categories(client, session, f_user, f_token, f_category):
    f_category("Caméras")
    token = f_token(f_user(AccessLevel.MANAGER))

    r = client.get("/api/io/categories/export", headers=auth(token))
    assert r.status_code == 200
    lines = r.text.splitlines()
    assert lines[0] == "id,name,description"
    assert any("Caméras" in line for line in lines[1:])


def test_import_categories_insert_and_update(client, session, f_user, f_token, f_category):
    existing = f_category("Ancien")
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "\n".join(
        [
            "id,name,description",
            f"{existing.id},Renommée,maj",  # update
            ",Toute neuve,,",  # insert (trailing extra comma tolerated)
        ]
    )
    r = client.post("/api/io/categories/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 200
    assert r.json() == {"created": 1, "updated": 1}

    updated = client.get(f"/api/categories/{existing.id}", headers=auth(token)).json()
    assert updated["name"] == "Renommée"


def test_import_categories_unknown_id_returns_422(client, session, f_user, f_token):
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "id,name\n4242,Fantôme"
    r = client.post("/api/io/categories/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    assert any("4242" in msg for msg in r.json()["detail"])


def test_export_items(client, session, f_user, f_token, f_category, f_catalog, f_item):
    cat = f_category()
    catalog = f_catalog(cat, "Sony A7")
    f_item(catalog, deposit_cents=5000)
    token = f_token(f_user(AccessLevel.MANAGER))

    r = client.get("/api/io/items/export", headers=auth(token))
    assert r.status_code == 200
    lines = r.text.splitlines()
    assert lines[0] == "id,name,catalog,condition,availability,deposit_eur"
    assert any("50.00" in line for line in lines[1:])


# ──────────────────────────────── import ─────────────────────────────────


def test_import_catalogs_insert_and_update(client, session, f_user, f_token, f_category, f_catalog):
    f_category("Caméras")
    existing = f_catalog(f_category("Son"), "Ancien nom")
    token = f_token(f_user(AccessLevel.MANAGER))

    csv_text = "\n".join(
        [
            "id,name,description,category",
            f"{existing.id},Nouveau nom,maj,Caméras",  # update (also moves category)
            ",Tout neuf,,Caméras",  # insert
        ]
    )
    r = client.post("/api/io/catalogs/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 200
    assert r.json() == {"created": 1, "updated": 1}

    updated = client.get(f"/api/catalogs/{existing.id}", headers=auth(token)).json()
    assert updated["name"] == "Nouveau nom"
    assert updated["category"]["name"] == "Caméras"


def test_import_catalogs_unknown_category_returns_422(client, session, f_user, f_token):
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "id,name,category\n,Objet,Inexistante"
    r = client.post("/api/io/catalogs/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    assert any("Inexistante" in msg for msg in r.json()["detail"])


def test_import_catalogs_unknown_id_returns_422(client, session, f_user, f_token, f_category):
    f_category("Caméras")
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "id,name,category\n9999,Objet,Caméras"
    r = client.post("/api/io/catalogs/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    assert any("9999" in msg for msg in r.json()["detail"])


def test_import_items_insert_converts_deposit(client, session, f_user, f_token, f_category, f_catalog):
    f_catalog(f_category(), "Sony A7")
    token = f_token(f_user(AccessLevel.MANAGER))

    csv_text = "\n".join(
        [
            "id,name,catalog,condition,availability,deposit_eur",
            ",Sony A7 #1,Sony A7,good,available,50.00",
        ]
    )
    r = client.post("/api/io/items/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 200
    assert r.json()["created"] == 1

    items = client.get("/api/items", headers=auth(token)).json()
    created = next(i for i in items if i["name"] == "Sony A7 #1")
    assert created["deposit_cents"] == 5000


def test_import_items_unknown_catalog_returns_422(client, session, f_user, f_token):
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "id,name,catalog,condition\n,X,CatalogueInconnu,good"
    r = client.post("/api/io/items/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    assert any("CatalogueInconnu" in msg for msg in r.json()["detail"])


def test_import_items_invalid_condition_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    f_catalog(f_category(), "Sony A7")
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "id,name,catalog,condition\n,X,Sony A7,banane"
    r = client.post("/api/io/items/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    assert any("banane" in msg for msg in r.json()["detail"])


def test_import_is_atomic_on_error(client, session, f_user, f_token, f_category, f_catalog):
    f_catalog(f_category(), "Sony A7")
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "\n".join(
        [
            "id,name,catalog,condition",
            ",Valide,Sony A7,good",  # valid
            ",Invalide,Inconnu,good",  # invalid catalog
        ]
    )
    r = client.post("/api/io/items/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    # Nothing committed: the valid row must not have been inserted.
    items = client.get("/api/items", headers=auth(token)).json()
    assert not any(i["name"] == "Valide" for i in items)


def test_import_missing_column_returns_422(client, session, f_user, f_token, f_category, f_catalog):
    f_catalog(f_category(), "Sony A7")
    token = f_token(f_user(AccessLevel.MANAGER))
    csv_text = "name,catalog\nX,Sony A7"  # missing 'condition'
    r = client.post("/api/io/items/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 422
    assert any("condition" in msg for msg in r.json()["detail"])


def test_import_requires_manager(client, session, f_user, f_token):
    token = f_token(f_user(AccessLevel.CLAP))
    r = client.post(
        "/api/io/items/import",
        files=_file("id,name,catalog,condition\n"),
        headers=auth(token),
    )
    assert r.status_code == 403


def test_import_semicolon_delimiter(client, session, f_user, f_token, f_category, f_catalog):
    f_catalog(f_category(), "Sony A7")
    token = f_token(f_user(AccessLevel.MANAGER))
    # French Excel style: semicolon delimiter, comma decimal.
    csv_text = "id;name;catalog;condition;deposit_eur\n;Sony A7 #1;Sony A7;good;50,00"
    r = client.post("/api/io/items/import", files=_file(csv_text), headers=auth(token))
    assert r.status_code == 200
    items = client.get("/api/items", headers=auth(token)).json()
    created = next(i for i in items if i["name"] == "Sony A7 #1")
    assert created["deposit_cents"] == 5000
