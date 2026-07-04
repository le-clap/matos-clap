"""CSV import / export for catalogs and items (manager only).

Import is an upsert keyed on the ``id`` column (empty id → insert, present id →
update); it never deletes. Every row is validated first: if any row is invalid
the whole import is rejected (HTTP 422) with one message per faulty line and
nothing is written. Foreign keys (category, catalog) are referenced by name.
"""

import csv
import io
from collections.abc import Mapping
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import require_role
from models.enums import AccessLevel, Availability, Condition
from models.models import Catalog, Category, Item, User

router = APIRouter(prefix="/io", tags=["import-export"])

SessionDep = Annotated[Session, Depends(get_session)]
ManagerDep = Annotated[User, Depends(require_role(AccessLevel.MANAGER))]


class ImportResult(BaseModel):
    created: int
    updated: int


# ──────────────────────────────── helpers ────────────────────────────────


def _parse_csv(raw: bytes) -> tuple[list[str], list[tuple[int, dict[str, str]]]]:
    """Return (header, [(line_number, row_dict), …]).

    Delimiter is auto-detected between ``,`` and ``;``. Header names are
    lower-cased and stripped. Blank lines are skipped. Line numbers are 1-based
    and account for the header row.
    """
    text = raw.decode("utf-8-sig", errors="replace")
    try:
        delimiter = csv.Sniffer().sniff(text[:2048], delimiters=",;").delimiter
    except csv.Error:
        delimiter = ","

    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    if not rows:
        return [], []

    header = [cell.strip().lower() for cell in rows[0]]
    records: list[tuple[int, dict[str, str]]] = []
    for line_number, raw_row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in raw_row):
            continue
        record = {header[i]: (raw_row[i].strip() if i < len(raw_row) else "") for i in range(len(header))}
        records.append((line_number, record))
    return header, records


def _missing_columns(header: list[str], required: tuple[str, ...]) -> list[str]:
    return [column for column in required if column not in header]


_CONDITION_VALUES = ", ".join(c.value for c in Condition)
_AVAILABILITY_VALUES = ", ".join(a.value for a in Availability)


# ──────────────────────────────── export ─────────────────────────────────


@router.get("/catalogs/export")
def export_catalogs(session: SessionDep, _user: ManagerDep) -> Response:
    catalogs = session.exec(
        select(Catalog).options(joinedload(Catalog.category))  # ty: ignore[invalid-argument-type]
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "description", "category", "image_path"])
    for catalog in catalogs:
        writer.writerow(
            [
                catalog.id,
                catalog.name,
                catalog.description or "",
                catalog.category.name,
                catalog.image_path or "",
            ]
        )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="catalogs.csv"'},
    )


@router.get("/categories/export")
def export_categories(session: SessionDep, _user: ManagerDep) -> Response:
    categories = session.exec(select(Category)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "description"])
    for category in categories:
        writer.writerow([category.id, category.name, category.description or ""])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="categories.csv"'},
    )


@router.get("/items/export")
def export_items(session: SessionDep, _user: ManagerDep) -> Response:
    items = session.exec(
        select(Item)
        .where(Item.deleted_at.is_(None))  # ty: ignore[unresolved-attribute]
        .options(joinedload(Item.catalog))  # ty: ignore[invalid-argument-type]
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "catalog", "condition", "availability", "deposit_eur"])
    for item in items:
        writer.writerow(
            [
                item.id,
                item.name,
                item.catalog.name,
                item.condition.value,
                item.availability.value,
                f"{item.deposit_cents / 100:.2f}",
            ]
        )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="items.csv"'},
    )


# ──────────────────────────────── import ─────────────────────────────────


def _index_by_name(rows: list) -> dict[str, list]:
    by_name: dict[str, list] = {}
    for row in rows:
        by_name.setdefault(row.name, []).append(row)
    return by_name


def _resolve_named(by_name: dict[str, list], value: str, line: int, label: str, errors: list[str]):
    """Resolve a unique row by name, appending an error and returning None on failure."""
    matches = by_name.get(value, [])
    if not matches:
        errors.append(f"Ligne {line} : {label} « {value} » introuvable")
        return None
    if len(matches) > 1:
        errors.append(f"Ligne {line} : {label} « {value} » ambigu(ë) ({len(matches)} correspondances)")
        return None
    return matches[0]


def _parse_id(id_raw: str, existing: Mapping[int, object], line: int, label: str, errors: list[str]):
    """Return (is_update, target). On error appends a message and returns (False, None)."""
    if not id_raw:
        return False, None
    if not id_raw.lstrip("-").isdigit():
        errors.append(f"Ligne {line} : id « {id_raw} » invalide")
        return False, None
    target = existing.get(int(id_raw))
    if target is None:
        errors.append(f"Ligne {line} : {label} id {id_raw} introuvable")
        return False, None
    return True, target


@router.post(
    "/categories/import",
    response_model=ImportResult,
    responses={422: {"description": "Validation errors (one message per faulty line)"}},
)
async def import_categories(
    session: SessionDep,
    _user: ManagerDep,
    file: Annotated[UploadFile, File()],
) -> ImportResult:
    header, records = _parse_csv(await file.read())
    missing = _missing_columns(header, ("name",))
    if missing:
        raise HTTPException(
            status_code=422,
            detail=[f"Colonne(s) obligatoire(s) manquante(s) : {', '.join(missing)}"],
        )

    existing = {c.id: c for c in session.exec(select(Category)).all() if c.id is not None}
    has_description = "description" in header

    errors: list[str] = []
    planned: list[tuple] = []  # (target|None, name, description?)

    for line, row in records:
        name = row.get("name", "")
        if not name:
            errors.append(f"Ligne {line} : le nom est obligatoire")
            continue

        is_update, target = _parse_id(row.get("id", ""), existing, line, "catégorie", errors)
        if row.get("id", "") and not is_update:
            continue

        planned.append((target, name, row.get("description", "") or None if has_description else None))

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    created = updated = 0
    for target, name, description in planned:
        if target is None:
            session.add(Category(name=name, description=description))
            created += 1
        else:
            target.name = name
            if has_description:
                target.description = description
            session.add(target)
            updated += 1

    session.commit()
    return ImportResult(created=created, updated=updated)


@router.post(
    "/catalogs/import",
    response_model=ImportResult,
    responses={422: {"description": "Validation errors (one message per faulty line)"}},
)
async def import_catalogs(
    session: SessionDep,
    _user: ManagerDep,
    file: Annotated[UploadFile, File()],
) -> ImportResult:
    header, records = _parse_csv(await file.read())
    missing = _missing_columns(header, ("name", "category"))
    if missing:
        raise HTTPException(
            status_code=422,
            detail=[f"Colonne(s) obligatoire(s) manquante(s) : {', '.join(missing)}"],
        )

    categories_by_name = _index_by_name(list(session.exec(select(Category)).all()))
    existing = {c.id: c for c in session.exec(select(Catalog)).all() if c.id is not None}

    has_description = "description" in header
    has_image = "image_path" in header

    errors: list[str] = []
    planned: list[tuple] = []  # (target|None, name, description?, category_id, image_path?)

    for line, row in records:
        name = row.get("name", "")
        category_name = row.get("category", "")
        if not name:
            errors.append(f"Ligne {line} : le nom est obligatoire")
            continue
        if not category_name:
            errors.append(f"Ligne {line} : la catégorie est obligatoire")
            continue

        category = _resolve_named(categories_by_name, category_name, line, "catégorie", errors)
        is_update, target = _parse_id(row.get("id", ""), existing, line, "catalogue", errors)
        if category is None or (row.get("id", "") and not is_update):
            continue

        planned.append(
            (
                target,
                name,
                row.get("description", "") or None if has_description else None,
                category.id,
                row.get("image_path", "") or None if has_image else None,
            )
        )

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    created = updated = 0
    for target, name, description, category_id, image_path in planned:
        if target is None:
            session.add(Catalog(name=name, description=description, category_id=category_id, image_path=image_path))
            created += 1
        else:
            target.name = name
            target.category_id = category_id
            if has_description:
                target.description = description
            if has_image:
                target.image_path = image_path
            session.add(target)
            updated += 1

    session.commit()
    return ImportResult(created=created, updated=updated)


@router.post(
    "/items/import",
    response_model=ImportResult,
    responses={422: {"description": "Validation errors (one message per faulty line)"}},
)
async def import_items(
    session: SessionDep,
    _user: ManagerDep,
    file: Annotated[UploadFile, File()],
) -> ImportResult:
    header, records = _parse_csv(await file.read())
    missing = _missing_columns(header, ("name", "catalog", "condition"))
    if missing:
        raise HTTPException(
            status_code=422,
            detail=[f"Colonne(s) obligatoire(s) manquante(s) : {', '.join(missing)}"],
        )

    catalogs_by_name = _index_by_name(list(session.exec(select(Catalog)).all()))
    existing = {
        i.id: i
        for i in session.exec(select(Item).where(Item.deleted_at.is_(None))).all()  # ty: ignore[unresolved-attribute]
        if i.id is not None
    }

    has_availability = "availability" in header
    has_deposit = "deposit_eur" in header

    errors: list[str] = []
    planned: list[tuple] = []  # (target|None, name, catalog_id, condition, availability?, deposit_cents?)

    for line, row in records:
        name = row.get("name", "")
        catalog_name = row.get("catalog", "")
        condition_raw = row.get("condition", "").lower()
        if not name:
            errors.append(f"Ligne {line} : le nom est obligatoire")
            continue
        if not catalog_name:
            errors.append(f"Ligne {line} : le catalogue est obligatoire")
            continue

        catalog = _resolve_named(catalogs_by_name, catalog_name, line, "catalogue", errors)
        is_update, target = _parse_id(row.get("id", ""), existing, line, "article", errors)

        condition: Condition | None = None
        if not condition_raw:
            errors.append(f"Ligne {line} : l'état est obligatoire")
        else:
            try:
                condition = Condition(condition_raw)
            except ValueError:
                errors.append(
                    f"Ligne {line} : état « {row.get('condition', '')} » invalide (valeurs : {_CONDITION_VALUES})"
                )

        availability = Availability.AVAILABLE
        if has_availability:
            availability_raw = row.get("availability", "").lower()
            if availability_raw:
                try:
                    availability = Availability(availability_raw)
                except ValueError:
                    errors.append(
                        f"Ligne {line} : disponibilité « {row.get('availability', '')} » invalide "
                        f"(valeurs : {_AVAILABILITY_VALUES})"
                    )

        deposit_cents = 0
        if has_deposit:
            deposit_raw = row.get("deposit_eur", "").replace(",", ".")
            if deposit_raw:
                try:
                    amount = float(deposit_raw)
                    if amount < 0:
                        raise ValueError
                    deposit_cents = round(amount * 100)
                except ValueError:
                    errors.append(f"Ligne {line} : caution « {row.get('deposit_eur', '')} » invalide")

        if catalog is None or condition is None or (row.get("id", "") and not is_update):
            continue

        planned.append(
            (
                target,
                name,
                catalog.id,
                condition,
                availability if has_availability else None,
                deposit_cents if has_deposit else None,
            )
        )

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    created = updated = 0
    for target, name, catalog_id, condition, availability, deposit_cents in planned:
        if target is None:
            session.add(
                Item(
                    name=name,
                    catalog_id=catalog_id,
                    condition=condition,
                    availability=availability or Availability.AVAILABLE,
                    deposit_cents=deposit_cents or 0,
                )
            )
            created += 1
        else:
            target.name = name
            target.catalog_id = catalog_id
            target.condition = condition
            if availability is not None:
                target.availability = availability
            if deposit_cents is not None:
                target.deposit_cents = deposit_cents
            session.add(target)
            updated += 1

    session.commit()
    return ImportResult(created=created, updated=updated)
