"""Item management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select

from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel, Availability, Condition, LoanStatus
from models.models import Catalog, Item, Loan, LoanedItem, User
from schemas.items import ItemHistoryEntry, ItemPatch, ItemPost, ItemPublic
from services.deletion import item_has_open_loan, purge_or_archive
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
    statement = select(Item).options(*item_load_options()).where(col(Item.deleted_at).is_(None))
    if availability is not None:
        statement = statement.where(Item.availability == availability)
    if condition is not None:
        statement = statement.where(Item.condition == condition)
    return list(session.exec(statement).all())


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


@router.get(
    "/{item_id}/history",
    response_model=list[ItemHistoryEntry],
    responses={404: {"description": "Item not found"}},
)
def get_item_history(
    session: SessionDep,
    _user: ClapDep,
    item_id: Annotated[int, Path(ge=1)],
) -> list[ItemHistoryEntry]:
    """Custody history of an item: every loan it was part of, most recent first."""
    if not session.get(Item, item_id):
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    effective_start = func.coalesce(Loan.actual_start_date, Loan.start_date)
    statement = (
        select(LoanedItem)
        .join(Loan, LoanedItem.loan_id == Loan.id)  # ty: ignore[invalid-argument-type]
        .where(LoanedItem.item_id == item_id)
        .options(
            joinedload(LoanedItem.loan).joinedload(Loan.borrower),  # ty: ignore[invalid-argument-type]
            joinedload(LoanedItem.loan).joinedload(Loan.assignee),  # ty: ignore[invalid-argument-type]
        )
        .order_by(effective_start.desc())
    )
    loaned_items = session.exec(statement).all()

    entries: list[ItemHistoryEntry] = []
    for li in loaned_items:
        loan = li.loan
        returned_at = li.actual_return_date or loan.actual_return_date
        if returned_at is not None:
            status = LoanStatus.RETURNED
        elif loan.actual_start_date is not None:
            status = LoanStatus.ACTIVE
        else:
            status = LoanStatus.SCHEDULED
        entries.append(
            ItemHistoryEntry(
                loan_id=loan.id,  # ty: ignore[invalid-argument-type]
                borrower=loan.borrower,  # ty: ignore[invalid-argument-type]
                assignee=loan.assignee,  # ty: ignore[invalid-argument-type]
                start_date=loan.start_date,
                end_date=loan.end_date,
                actual_start_date=loan.actual_start_date,
                actual_return_date=returned_at,
                return_condition=li.return_condition,
                status=status,
            )
        )
    return entries


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
    catalog = session.get(Catalog, item.catalog_id)
    if not catalog or catalog.deleted_at is not None:
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
    if not db_item or db_item.deleted_at is not None:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    update_data = item_patch.model_dump(exclude_unset=True)
    if "catalog_id" in update_data:
        catalog = session.get(Catalog, update_data["catalog_id"])
        if not catalog or catalog.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Catalog with ID {update_data['catalog_id']} not found")

    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Item not found"},
        409: {"description": "Item is part of an active or scheduled loan"},
    },
)
def delete_item(
    session: SessionDep,
    _user: ManagerDep,
    item_id: Annotated[int, Path(ge=1)],
) -> None:
    item = session.get(Item, item_id, with_for_update=True)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    if item_has_open_loan(session, item_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete item: it is part of an active or scheduled loan",
        )

    purge_or_archive(session, Item, item_id)
