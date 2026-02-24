from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from db.database import get_session
from models.enums import Availability
from models.models import Catalog, Category, Item, Loan, LoanedItem
from schemas.catalog import CatalogPatch, CatalogPost, CatalogPublic
from schemas.item import ItemAvailabilityResponse

router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)


@router.get("/", response_model=list[CatalogPublic])
def get_catalogs(session: Session = Depends(get_session)):
    statement = select(Catalog).options(joinedload(Catalog.category))  # ty: ignore[invalid-argument-type]
    return session.exec(statement).all()


@router.get(
    "/{catalog_id}",
    response_model=CatalogPublic,
    responses={404: {"description": "Catalog not found"}},
)
def get_catalog_by_id(catalog_id: int, session: Session = Depends(get_session)):
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
def create_catalog(catalog: CatalogPost, session: Session = Depends(get_session)):
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
    catalog_id: int,
    catalog_patch: CatalogPatch,
    session: Session = Depends(get_session),
):
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    update_data = catalog_patch.model_dump(exclude_unset=True)

    if "category_id" in update_data and not session.get(Category, update_data["category_id"]):
        raise HTTPException(status_code=404, detail=f"Category with ID {update_data['category_id']} not found")

    db_catalog.sqlmodel_update(update_data)
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
def delete_catalog(catalog_id: int, session: Session = Depends(get_session)):
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


def _item_load_options():
    return [
        joinedload(Item.catalog).joinedload(Catalog.category),  # ty: ignore[invalid-argument-type]
    ]


@router.get(
    "/{catalog_id}/items/availability",
    response_model=ItemAvailabilityResponse,
    responses={
        404: {"description": "Catalog not found"},
        422: {"description": "Invalid date range"},
    },
)
def get_catalog_items_availability(
    catalog_id: int,
    start_date: datetime = Query(),
    end_date: datetime = Query(),
    session: Session = Depends(get_session),
):
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

    all_items = (
        session.exec(
            select(Item)
            .where(Item.catalog_id == catalog_id, Item.deleted == False)  # noqa: E712
            .options(*_item_load_options())
        )
        .unique()
        .all()
    )

    # Item IDs with an overlapping active loan
    item_ids = [item.id for item in all_items]
    busy_ids: set[int] = set()
    if item_ids:
        busy_stmt = (
            select(LoanedItem.item_id)
            .join(Loan, LoanedItem.loan_id == Loan.id)  # ty: ignore[invalid-argument-type]
            .where(
                LoanedItem.item_id.in_(item_ids),  # type: ignore[union-attr]
                Loan.actual_return_date.is_(None),  # type: ignore[union-attr]
                Loan.start_date < end_date,
                Loan.end_date > start_date,
            )
        )
        busy_ids = set(session.exec(busy_stmt).all())

    available: list[Item] = []
    unavailable: list[Item] = []
    for item in all_items:
        if item.availability == Availability.AVAILABLE and item.id not in busy_ids:
            available.append(item)
        else:
            unavailable.append(item)

    return ItemAvailabilityResponse(available=available, unavailable=unavailable)  # ty: ignore[invalid-argument-type]
