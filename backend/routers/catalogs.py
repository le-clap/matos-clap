"""Catalog management endpoints."""

import uuid
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile, status
from pydantic import AwareDatetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select

from core.config import settings
from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel, Availability
from models.models import Catalog, Category, Item, User
from schemas.catalogs import CatalogPatch, CatalogPost, CatalogPublic
from schemas.items import ItemAvailabilityResponse
from services.inventory import find_busy_item_ids, item_load_options

router = APIRouter(prefix="/catalogs", tags=["catalogs"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ManagerDep = Annotated[User, Depends(require_role(AccessLevel.MANAGER))]

# Allowed image content types mapped to their file extension.
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.get("/", response_model=list[CatalogPublic])
def get_catalogs(session: SessionDep, _user: CurrentUserDep) -> list[Catalog]:
    statement = select(Catalog).options(joinedload(Catalog.category))  # ty: ignore[invalid-argument-type]
    return list(session.exec(statement).all())


@router.get(
    "/{catalog_id}",
    response_model=CatalogPublic,
    responses={404: {"description": "Catalog not found"}},
)
def get_catalog_by_id(
    session: SessionDep,
    _user: CurrentUserDep,
    catalog_id: Annotated[int, Path(ge=1)],
) -> Catalog:
    statement = (
        select(Catalog)
        .where(Catalog.id == catalog_id)
        .options(
            joinedload(Catalog.category)  # ty: ignore[invalid-argument-type]
        )
    )
    catalog = session.exec(statement).first()
    if not catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")
    return catalog


@router.post(
    "/",
    response_model=CatalogPublic,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Category not found"}},
)
def create_catalog(
    session: SessionDep,
    _user: ManagerDep,
    catalog: CatalogPost,
) -> Catalog:
    if not session.get(Category, catalog.category_id):
        raise HTTPException(status_code=404, detail=f"Category with ID {catalog.category_id} not found")

    db_catalog = Catalog(**catalog.model_dump())
    session.add(db_catalog)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.patch(
    "/{catalog_id}",
    response_model=CatalogPublic,
    responses={404: {"description": "Catalog or referenced category not found"}},
)
def update_catalog(
    session: SessionDep,
    _user: ManagerDep,
    catalog_id: Annotated[int, Path(ge=1)],
    catalog_patch: CatalogPatch,
) -> Catalog:
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    update_data = catalog_patch.model_dump(exclude_unset=True)

    if "category_id" in update_data and not session.get(Category, update_data["category_id"]):
        raise HTTPException(status_code=404, detail=f"Category with ID {update_data['category_id']} not found")

    # If the image is being replaced or cleared, remove the previous file.
    if "image_path" in update_data:
        previous = db_catalog.image_path
        if previous and previous != update_data["image_path"] and previous.startswith("/media/catalogs/"):
            (FilePath(settings.MEDIA_DIR) / "catalogs" / FilePath(previous).name).unlink(missing_ok=True)

    db_catalog.sqlmodel_update(update_data)
    session.add(db_catalog)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.post(
    "/{catalog_id}/image",
    response_model=CatalogPublic,
    responses={
        404: {"description": "Catalog not found"},
        422: {"description": "Unsupported or oversized image"},
    },
)
async def upload_catalog_image(
    session: SessionDep,
    _user: ManagerDep,
    catalog_id: Annotated[int, Path(ge=1)],
    file: Annotated[UploadFile, File()],
) -> Catalog:
    """Upload (or replace) the illustrative image of a catalog reference."""
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(status_code=422, detail="Unsupported image type (use JPEG, PNG, WebP or GIF)")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=422, detail="Image exceeds the 5 MB size limit")

    catalogs_media_dir = FilePath(settings.MEDIA_DIR) / "catalogs"
    catalogs_media_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{extension}"
    (catalogs_media_dir / filename).write_bytes(contents)

    # Best-effort removal of the previously stored image to avoid orphans.
    previous = db_catalog.image_path
    if previous and previous.startswith("/media/catalogs/"):
        (catalogs_media_dir / FilePath(previous).name).unlink(missing_ok=True)

    db_catalog.image_path = f"/media/catalogs/{filename}"
    session.add(db_catalog)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.delete(
    "/{catalog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Catalog not found"},
        409: {"description": "Catalog still used by items or requests"},
    },
)
def delete_catalog(
    session: SessionDep,
    _user: ManagerDep,
    catalog_id: Annotated[int, Path(ge=1)],
) -> None:
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    try:
        session.delete(db_catalog)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete catalog: still used by items or requests",
        ) from e


@router.get(
    "/{catalog_id}/available-items",
    response_model=ItemAvailabilityResponse,
    responses={
        404: {"description": "Catalog not found"},
        422: {"description": "Invalid date range"},
    },
)
def get_catalog_items_availability(
    session: SessionDep,
    _user: CurrentUserDep,
    catalog_id: Annotated[int, Path(ge=1)],
    start_date: Annotated[AwareDatetime, Query()],
    end_date: Annotated[AwareDatetime, Query()],
) -> ItemAvailabilityResponse:
    """Return items split by availability for the requested date range.

    An item is **available** if it is not deleted, has availability status
    ``AVAILABLE``, and is not loaned for any part of [start_date, end_date].
    All other non-deleted items are returned in the **unavailable** list
    so an admin can still force-assign them.
    """
    if start_date >= end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")

    if not session.get(Catalog, catalog_id):
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    all_items = session.exec(
        select(Item).where(Item.catalog_id == catalog_id, col(Item.deleted_at).is_(None)).options(*item_load_options())
    ).all()

    item_ids = [item.id for item in all_items if item.id is not None]
    busy_ids = find_busy_item_ids(session, item_ids, start_date, end_date)

    available: list[Item] = []
    unavailable: list[Item] = []
    for item in all_items:
        if item.availability == Availability.AVAILABLE and item.id not in busy_ids:
            available.append(item)
        else:
            unavailable.append(item)

    return ItemAvailabilityResponse(available=available, unavailable=unavailable)  # ty: ignore[invalid-argument-type]
