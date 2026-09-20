"""Catalog management endpoints."""

import uuid
from pathlib import Path as FilePath
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile, status
from pydantic import AwareDatetime
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, col, select

from core.config import settings
from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel, Availability
from models.models import Catalog, CatalogImage, Category, Item, User
from schemas.catalogs import CatalogImageOrder, CatalogPatch, CatalogPost, CatalogPublic
from schemas.items import ItemAvailabilityResponse
from services.deletion import has_live_children, purge_or_archive
from services.inventory import find_busy_item_ids, item_load_options

logger = structlog.get_logger(__name__)

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


def _delete_media_file(image_path: str) -> None:
    """Best-effort removal of a stored catalog image file from disk."""
    if image_path.startswith("/media/catalogs/"):
        (FilePath(settings.MEDIA_DIR) / "catalogs" / FilePath(image_path).name).unlink(missing_ok=True)


@router.get("/", response_model=list[CatalogPublic])
def get_catalogs(session: SessionDep, _user: CurrentUserDep) -> list[Catalog]:
    statement = (
        select(Catalog)
        .where(col(Catalog.deleted_at).is_(None))
        .options(
            joinedload(Catalog.category),  # ty: ignore[invalid-argument-type]
            selectinload(Catalog.images),  # ty: ignore[invalid-argument-type]
        )
    )
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
            joinedload(Catalog.category),  # ty: ignore[invalid-argument-type]
            selectinload(Catalog.images),  # ty: ignore[invalid-argument-type]
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
    category = session.get(Category, catalog.category_id)
    if not category or category.deleted_at is not None:
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
    if not db_catalog or db_catalog.deleted_at is not None:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    update_data = catalog_patch.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = session.get(Category, update_data["category_id"])
        if not category or category.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Category with ID {update_data['category_id']} not found")

    db_catalog.sqlmodel_update(update_data)
    session.add(db_catalog)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.post(
    "/{catalog_id}/images",
    response_model=CatalogPublic,
    status_code=status.HTTP_201_CREATED,
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
    """Add an image to a catalog reference's gallery."""
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog or db_catalog.deleted_at is not None:
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

    # max(...) + 1, not len(...): a prior delete can leave positions with gaps
    # (e.g. [0, 2]), and len() would collide with a surviving position.
    next_position = max((image.position for image in db_catalog.images), default=-1) + 1
    db_image = CatalogImage(
        catalog_id=catalog_id,
        image_path=f"/media/catalogs/{filename}",
        position=next_position,
    )
    session.add(db_image)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.delete(
    "/{catalog_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Image not found on this catalog"}},
)
def delete_catalog_image(
    session: SessionDep,
    _user: ManagerDep,
    catalog_id: Annotated[int, Path(ge=1)],
    image_id: Annotated[int, Path(ge=1)],
) -> None:
    """Remove one image from a catalog's gallery."""
    db_image = session.get(CatalogImage, image_id)
    if not db_image or db_image.catalog_id != catalog_id:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found on catalog {catalog_id}")

    image_path = db_image.image_path
    session.delete(db_image)
    session.commit()
    _delete_media_file(image_path)


@router.put(
    "/{catalog_id}/images/order",
    response_model=CatalogPublic,
    responses={
        404: {"description": "Catalog not found"},
        422: {"description": "image_ids must match the catalog's existing images"},
    },
)
def reorder_catalog_images(
    session: SessionDep,
    _user: ManagerDep,
    catalog_id: Annotated[int, Path(ge=1)],
    order: CatalogImageOrder,
) -> Catalog:
    """Reorder a catalog's gallery to match the given list of image IDs."""
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog or db_catalog.deleted_at is not None:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    by_id = {image.id: image for image in db_catalog.images}
    if set(order.image_ids) != set(by_id) or len(order.image_ids) != len(by_id):
        raise HTTPException(status_code=422, detail="image_ids must match the catalog's existing images exactly")

    for position, image_id in enumerate(order.image_ids):
        by_id[image_id].position = position
    session.add_all(by_id.values())
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
    db_catalog = session.get(Catalog, catalog_id, with_for_update=True)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    if has_live_children(session, Item, col(Item.catalog_id), catalog_id):
        logger.warning("catalog.delete_blocked", catalog_id=catalog_id)
        raise HTTPException(
            status_code=409,
            detail="Cannot delete catalog: it still contains items",
        )

    image_paths = [image.image_path for image in db_catalog.images]
    purged = purge_or_archive(session, Catalog, catalog_id)

    if purged:
        for image_path in image_paths:
            _delete_media_file(image_path)


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

    catalog = session.get(Catalog, catalog_id)
    if not catalog or catalog.deleted_at is not None:
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
