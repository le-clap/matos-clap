"""Item management endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel, Availability, Condition, LoanStatus
from models.models import Catalog, Item, Loan, LoanedItem, User
from schemas.items import ItemPatch, ItemPost, ItemPublic, LoanedItemsResponse, LoanedItemWithLoan
from services.inventory import item_load_options

router = APIRouter(prefix="/items", tags=["items"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ClapDep = Annotated[User, Depends(require_role(AccessLevel.CLAP))]
ManagerDep = Annotated[User, Depends(require_role(AccessLevel.MANAGER))]


@router.get("/", response_model=list[ItemPublic])
def get_items(
    session: SessionDep,
    _user: CurrentUserDep,
    availability: Annotated[Availability | None, Query()] = None,
    condition: Annotated[Condition | None, Query()] = None,
) -> list[Item]:
    statement = (
        select(Item).options(*item_load_options()).where(Item.deleted_at.is_(None))  # ty: ignore[unresolved-attribute]
    )
    if availability is not None:
        statement = statement.where(Item.availability == availability)
    if condition is not None:
        statement = statement.where(Item.condition == condition)
    return list(session.exec(statement).unique().all())


@router.get(
    "/loaned",
    response_model=LoanedItemsResponse,
    responses={422: {"description": "Invalid date range"}},
)
def get_loaned_items(
    session: SessionDep,
    _user: ClapDep,
    start_date: Annotated[datetime, Query(description="Start of the date range")],
    end_date: Annotated[datetime, Query(description="End of the date range")],
) -> LoanedItemsResponse:
    """Get all items that are loaned out during a date range.

    Returns items with their associated loan information, useful for
    seeing what equipment is out at any given time.
    """
    if start_date >= end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")

    effective_start = func.coalesce(Loan.actual_start_date, Loan.start_date)
    effective_end = func.coalesce(LoanedItem.actual_return_date, Loan.actual_return_date, Loan.end_date)

    statement = (
        select(LoanedItem)
        .join(Loan, LoanedItem.loan_id == Loan.id)  # ty: ignore[invalid-argument-type]
        .join(Item, LoanedItem.item_id == Item.id)  # ty: ignore[invalid-argument-type]
        .options(
            joinedload(LoanedItem.item).joinedload(Item.catalog),  # ty: ignore[invalid-argument-type]
            joinedload(LoanedItem.loan).joinedload(Loan.borrower),  # ty: ignore[invalid-argument-type]
        )
        .where(
            Item.deleted_at.is_(None),  # ty: ignore[unresolved-attribute]
            effective_start < end_date,
            effective_end > start_date,
        )
        .order_by(effective_start)
    )
    loaned_items = session.exec(statement).unique().all()

    def get_status(loan: Loan) -> LoanStatus:
        if loan.actual_return_date is not None:
            return LoanStatus.RETURNED
        if loan.actual_start_date is not None:
            return LoanStatus.ACTIVE
        return LoanStatus.SCHEDULED

    items_with_loans = [
        LoanedItemWithLoan(
            item_id=li.item.id,  # ty: ignore[invalid-argument-type]
            item_name=li.item.name,
            catalog_name=li.item.catalog.name,
            loan_id=li.loan.id,  # ty: ignore[invalid-argument-type]
            borrower_name=li.loan.borrower.name,
            loan_start_date=li.loan.start_date,
            loan_end_date=li.loan.end_date,
            actual_start_date=li.loan.actual_start_date,
            actual_return_date=li.actual_return_date or li.loan.actual_return_date,
            status=get_status(li.loan),
        )
        for li in loaned_items
    ]

    return LoanedItemsResponse(
        start_date=start_date,
        end_date=end_date,
        loaned_items=items_with_loans,
    )


@router.get(
    "/{item_id}",
    response_model=ItemPublic,
    responses={404: {"description": "Item not found"}},
)
def get_item_by_id(
    session: SessionDep,
    _user: CurrentUserDep,
    item_id: Annotated[int, Path(ge=1)],
) -> Item:
    statement = select(Item).where(Item.id == item_id).options(*item_load_options())
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return item


@router.post(
    "/",
    response_model=ItemPublic,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Referenced catalog not found"}},
)
def create_item(
    session: SessionDep,
    _user: ManagerDep,
    item: ItemPost,
) -> Item:
    if not session.get(Catalog, item.catalog_id):
        raise HTTPException(status_code=404, detail=f"Catalog with ID {item.catalog_id} not found")

    db_item = Item(**item.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.patch(
    "/{item_id}",
    response_model=ItemPublic,
    responses={404: {"description": "Item or referenced catalog not found"}},
)
def update_item(
    session: SessionDep,
    _user: ManagerDep,
    item_id: Annotated[int, Path(ge=1)],
    item_patch: ItemPatch,
) -> Item:
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    update_data = item_patch.model_dump(exclude_unset=True)
    if "catalog_id" in update_data and not session.get(Catalog, update_data["catalog_id"]):
        raise HTTPException(status_code=404, detail=f"Catalog with ID {update_data['catalog_id']} not found")

    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Item not found"}},
)
def soft_delete_item(
    session: SessionDep,
    _user: ManagerDep,
    item_id: Annotated[int, Path(ge=1)],
) -> None:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    item.deleted_at = datetime.now(UTC)
    session.add(item)
    session.commit()
