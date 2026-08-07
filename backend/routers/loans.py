"""Loan management endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import AwareDatetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, asc, col, select

from db.database import get_session
from dependencies.auth import get_current_user, has_role, require_role
from models.enums import AccessLevel, Condition, LoanStatus, RequestStatus
from models.models import Item, Loan, LoanedItem, Request, User
from schemas.loans import (
    LoanPartialReturnPost,
    LoanPatch,
    LoanPost,
    LoanPostResponse,
    LoanPostWarning,
    LoanPublic,
    LoanReturnPost,
)
from schemas.timeline import LoanTimelineEntry, LoanTimelineResponse
from schemas.utils import PaginatedResponse, PaginationParams
from services.inventory import find_busy_item_ids

router = APIRouter(prefix="/loans", tags=["loans"])


def _ensure_aware(dt: datetime) -> datetime:
    """Normalize a potentially naive datetime to UTC-aware."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ClapDep = Annotated[User, Depends(require_role(AccessLevel.CLAP))]


def _loan_load_options():
    return [
        joinedload(Loan.borrower),  # ty: ignore[invalid-argument-type]
        joinedload(Loan.assignee),  # ty: ignore[invalid-argument-type]
        selectinload(Loan.loaned_items).joinedload(LoanedItem.item),  # ty: ignore[invalid-argument-type]
    ]


@router.get("/", response_model=PaginatedResponse[LoanPublic])
def get_loans(
    session: SessionDep,
    current_user: CurrentUserDep,
    pagination: Annotated[PaginationParams, Depends()],
    borrower_id: Annotated[int | None, Query()] = None,
    status: Annotated[LoanStatus | None, Query()] = None,
) -> PaginatedResponse[Loan]:
    effective_borrower_id = borrower_id
    if not has_role(current_user, AccessLevel.CLAP):
        effective_borrower_id = current_user.id
    if effective_borrower_id is not None and not session.get(User, effective_borrower_id):
        raise HTTPException(status_code=404, detail=f"User with ID {effective_borrower_id} not found")

    base_statement = select(Loan)
    if effective_borrower_id is not None:
        base_statement = base_statement.where(Loan.borrower_id == effective_borrower_id)
    elif pagination.search is not None:
        base_statement = base_statement.join(Loan.borrower).where(  # ty: ignore[invalid-argument-type]
            col(User.name).ilike(f"%{pagination.search}%")
        )
    if status is not None:
        base_statement = base_statement.where(Loan.status == status)

    total = session.exec(select(func.count()).select_from(base_statement.subquery())).one()

    statement = (
        base_statement.options(*_loan_load_options())
        .order_by(asc(Loan.start_date), asc(Loan.id))
        .offset(pagination.offset())
        .limit(pagination.limit)
    )
    loans = session.exec(statement).all()

    return PaginatedResponse(
        items=list(loans),
        total=total,
        limit=pagination.limit,
        page=pagination.page,
        search=pagination.search,
    )


@router.get(
    "/timeline",
    response_model=LoanTimelineResponse,
    responses={422: {"description": "Invalid date range"}},
)
def get_loans_timeline(
    session: SessionDep,
    _user: ClapDep,
    start_date: Annotated[AwareDatetime, Query(description="Start of the date range")],
    end_date: Annotated[AwareDatetime, Query(description="End of the date range")],
) -> LoanTimelineResponse:
    """Get all loans overlapping a date range for calendar/timeline display.

    Returns loans that have any overlap with [start_date, end_date], including:
    - Loans that start before and end during the range
    - Loans entirely within the range
    - Loans that start during and end after the range
    - Loans that span the entire range
    """
    if start_date >= end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")

    effective_start = func.coalesce(Loan.actual_start_date, Loan.start_date)
    effective_end = func.coalesce(Loan.actual_return_date, Loan.end_date)

    statement = (
        select(Loan)
        .options(*_loan_load_options())
        .where(
            effective_start < end_date,
            effective_end > start_date,
        )
        .order_by(effective_start)
    )
    loans = session.exec(statement).all()

    timeline_entries = [
        LoanTimelineEntry(
            loan_id=loan.id,  # ty: ignore[invalid-argument-type]
            borrower=loan.borrower,  # ty: ignore[invalid-argument-type]
            assignee=loan.assignee,  # ty: ignore[invalid-argument-type]
            start_date=loan.start_date,
            end_date=loan.end_date,
            actual_start_date=loan.actual_start_date,
            actual_return_date=loan.actual_return_date,
            status=loan.status,
            items=[item.item for item in loan.loaned_items],  # ty: ignore[invalid-argument-type]
        )
        for loan in loans
    ]

    return LoanTimelineResponse(
        start_date=start_date,
        end_date=end_date,
        loans=timeline_entries,
    )


@router.get(
    "/{loan_id}",
    response_model=LoanPublic,
    responses={404: {"description": "Loan not found"}},
)
def get_loan_by_id(
    session: SessionDep,
    current_user: CurrentUserDep,
    loan_id: Annotated[int, Path(ge=1)],
) -> Loan:
    statement = select(Loan).where(Loan.id == loan_id).options(*_loan_load_options())
    loan = session.exec(statement).first()
    if not loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")
    if not has_role(current_user, AccessLevel.CLAP) and loan.borrower_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return loan


@router.post(
    "/",
    response_model=LoanPostResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Referenced user, request, or item not found"},
        422: {"description": "Invalid payload"},
    },
)
def create_loan(
    session: SessionDep,
    current_user: ClapDep,
    payload: LoanPost,
) -> LoanPostResponse:
    if not session.get(User, payload.borrower_id):
        raise HTTPException(status_code=404, detail=f"Borrower with ID {payload.borrower_id} not found")

    assignee_id = payload.assignee_id or current_user.id
    if assignee_id is None:
        raise HTTPException(status_code=500, detail="Unable to infer assignee_id from current user")
    if not session.get(User, assignee_id):
        raise HTTPException(status_code=404, detail=f"Assignee with ID {assignee_id} not found")

    db_request: Request | None = None
    if payload.request_id is not None:
        db_request = session.get(Request, payload.request_id)
        if not db_request:
            raise HTTPException(status_code=404, detail=f"Request with ID {payload.request_id} not found")
        if db_request.borrower_id != payload.borrower_id:
            raise HTTPException(
                status_code=422,
                detail="request_id borrower does not match borrower_id",
            )
        if db_request.loan is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Request {payload.request_id} has already been turned into loan {db_request.loan.id}",
            )
        if db_request.refused:
            raise HTTPException(
                status_code=409,
                detail=f"Request {payload.request_id} has been refused; reopen it before creating a loan",
            )

    unique_item_ids = list(dict.fromkeys(payload.item_ids))
    if len(unique_item_ids) != len(payload.item_ids):
        raise HTTPException(status_code=422, detail="Duplicate item IDs are not allowed")

    items = session.exec(select(Item).where(col(Item.id).in_(unique_item_ids))).all()
    item_by_id = {item.id: item for item in items if item.id is not None}
    missing_item_ids = [item_id for item_id in unique_item_ids if item_id not in item_by_id]
    if missing_item_ids:
        raise HTTPException(status_code=404, detail=f"Item(s) not found: {missing_item_ids}")

    deleted_item_ids = [item.id for item in items if item.id is not None and item.deleted_at is not None]
    if deleted_item_ids:
        raise HTTPException(status_code=422, detail=f"Deleted item(s) cannot be assigned: {deleted_item_ids}")

    warnings: list[LoanPostWarning] = []
    busy_item_ids = find_busy_item_ids(session, unique_item_ids, payload.start_date, payload.end_date)
    for item_id in unique_item_ids:
        if item_id in busy_item_ids:
            warnings.append(
                LoanPostWarning(
                    code="ITEM_DATE_CONFLICT",
                    message=f"Item {item_id} overlaps with another active loan for this date range",
                    item_id=item_id,
                )
            )

    db_loan = Loan(
        borrower_id=payload.borrower_id,
        assignee_id=assignee_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_deposit_cents=payload.total_deposit_cents,
        request_id=payload.request_id,
        comments=payload.comments,
    )
    session.add(db_loan)
    session.flush()
    if db_loan.id is None:
        raise HTTPException(status_code=500, detail="Failed to create loan")

    for item_id in unique_item_ids:
        session.add(LoanedItem(loan_id=db_loan.id, item_id=item_id))

    if db_request is not None:
        db_request.status = RequestStatus.APPROVED
        session.add(db_request)

    session.commit()

    created_loan = session.exec(select(Loan).where(Loan.id == db_loan.id).options(*_loan_load_options())).first()
    if not created_loan:
        raise HTTPException(status_code=500, detail="Loan was created but could not be reloaded")
    return LoanPostResponse(loan=created_loan, warnings=warnings)  # ty: ignore[invalid-argument-type]


@router.post(
    "/{loan_id}/partial-return",
    response_model=LoanPublic,
    responses={
        404: {"description": "Loan not found"},
        409: {"description": "Loan not started or already returned"},
        422: {"description": "Invalid partial return payload"},
    },
)
def partial_return_loan_items(
    session: SessionDep,
    _user: ClapDep,
    loan_id: Annotated[int, Path(ge=1)],
    partial_return_data: LoanPartialReturnPost,
) -> Loan:
    statement = select(Loan).where(Loan.id == loan_id).options(*_loan_load_options())
    db_loan = session.exec(statement).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")
    if db_loan.actual_start_date is None:
        raise HTTPException(status_code=409, detail=f"Loan with ID {loan_id} has not been started yet")
    if db_loan.actual_return_date is not None:
        raise HTTPException(status_code=409, detail=f"Loan with ID {loan_id} is already returned")

    payload_item_ids = [item.item_id for item in partial_return_data.items]
    unique_item_ids = list(dict.fromkeys(payload_item_ids))
    if len(unique_item_ids) != len(payload_item_ids):
        raise HTTPException(status_code=422, detail="Duplicate item_id values are not allowed")

    loaned_item_by_item_id = {loaned_item.item_id: loaned_item for loaned_item in db_loan.loaned_items}
    unknown_item_ids = [item_id for item_id in unique_item_ids if item_id not in loaned_item_by_item_id]
    if unknown_item_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Some items are not present in this loan: {unknown_item_ids}",
        )

    already_returned_ids = [
        item_id for item_id in unique_item_ids if loaned_item_by_item_id[item_id].actual_return_date is not None
    ]
    if already_returned_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Some items were already partially returned: {already_returned_ids}",
        )

    returned_at = datetime.now(UTC)
    if returned_at < _ensure_aware(db_loan.actual_start_date):
        raise HTTPException(status_code=422, detail="Partial return date cannot be before actual_start_date")

    for item in partial_return_data.items:
        db_loaned_item = loaned_item_by_item_id[item.item_id]
        db_loaned_item.actual_return_date = returned_at
        if item.return_condition is not None:
            db_loaned_item.return_condition = item.return_condition
        session.add(db_loaned_item)

    remaining_items = [loaned_item for loaned_item in db_loan.loaned_items if loaned_item.actual_return_date is None]
    if not remaining_items:
        raise HTTPException(
            status_code=422,
            detail="Partial return must leave at least one loaned item still active",
        )

    session.commit()
    session.refresh(db_loan)
    return db_loan


@router.post(
    "/{loan_id}/return",
    response_model=LoanPublic,
    responses={
        404: {"description": "Loan not found"},
        409: {"description": "Loan not started or already returned"},
        422: {"description": "Invalid return payload"},
    },
)
def return_loan(
    session: SessionDep,
    _user: ClapDep,
    loan_id: Annotated[int, Path(ge=1)],
    return_data: LoanReturnPost,
) -> Loan:
    statement = select(Loan).where(Loan.id == loan_id).options(*_loan_load_options())
    db_loan = session.exec(statement).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")
    if db_loan.actual_start_date is None:
        raise HTTPException(status_code=409, detail=f"Loan with ID {loan_id} has not been started yet")
    if db_loan.actual_return_date is not None:
        raise HTTPException(status_code=409, detail=f"Loan with ID {loan_id} is already returned")
    if return_data.retained_deposit_cents > db_loan.total_deposit_cents:
        raise HTTPException(status_code=422, detail="retained_deposit_cents cannot exceed total_deposit_cents")

    if return_data.item_return_conditions:
        condition_by_item_id: dict[int, Condition] = {}
        for item_condition in return_data.item_return_conditions:
            if item_condition.item_id in condition_by_item_id:
                raise HTTPException(status_code=422, detail=f"Duplicate item_id in payload: {item_condition.item_id}")
            condition_by_item_id[item_condition.item_id] = item_condition.return_condition

        loaned_item_by_item_id = {loaned_item.item_id: loaned_item for loaned_item in db_loan.loaned_items}
        unknown_item_ids = [item_id for item_id in condition_by_item_id if item_id not in loaned_item_by_item_id]
        if unknown_item_ids:
            raise HTTPException(
                status_code=422,
                detail=f"Some item_return_conditions refer to items not present in this loan: {unknown_item_ids}",
            )

        for item_id, condition in condition_by_item_id.items():
            db_loaned_item = loaned_item_by_item_id[item_id]
            db_loaned_item.return_condition = condition
            session.add(db_loaned_item)

    returned_at = datetime.now(UTC)
    if returned_at < _ensure_aware(db_loan.actual_start_date):
        raise HTTPException(status_code=422, detail="Return date cannot be before actual_start_date")

    for loaned_item in db_loan.loaned_items:
        if loaned_item.actual_return_date is not None and _ensure_aware(loaned_item.actual_return_date) > returned_at:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Loaned item {loaned_item.item_id} has actual_return_date after loan return date, "
                    "which violates return ordering"
                ),
            )
        if loaned_item.actual_return_date is None:
            loaned_item.actual_return_date = returned_at
            session.add(loaned_item)

    db_loan.actual_return_date = returned_at
    db_loan.retained_deposit_cents = return_data.retained_deposit_cents
    if return_data.comments is not None:
        db_loan.comments = return_data.comments

    session.add(db_loan)
    session.commit()
    session.refresh(db_loan)
    return db_loan


@router.patch(
    "/{loan_id}",
    response_model=LoanPublic,
    responses={404: {"description": "Loan not found"}},
)
def update_loan(
    session: SessionDep,
    _user: ClapDep,
    loan_id: Annotated[int, Path(ge=1)],
    loan_patch: LoanPatch,
) -> Loan:
    db_loan = session.exec(select(Loan).where(Loan.id == loan_id).options(*_loan_load_options())).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")

    update_data = loan_patch.model_dump(exclude_unset=True)
    new_item_ids = update_data.pop("item_ids", None)
    changes_borrower = "borrower_id" in update_data and update_data["borrower_id"] != db_loan.borrower_id

    # The resulting period must stay valid even when only one bound is patched.
    new_start = loan_patch.start_date or db_loan.start_date
    new_end = loan_patch.end_date or db_loan.end_date
    if _ensure_aware(new_start) >= _ensure_aware(new_end):
        raise HTTPException(status_code=422, detail="start_date must be before end_date")

    # Structural edits (items, borrower) are only allowed before the loan starts.
    if (new_item_ids is not None or changes_borrower) and db_loan.actual_start_date is not None:
        raise HTTPException(
            status_code=409,
            detail="A started loan's items and borrower can no longer be changed",
        )

    if changes_borrower and not session.get(User, update_data["borrower_id"]):
        raise HTTPException(status_code=404, detail=f"Borrower with ID {update_data['borrower_id']} not found")

    if new_item_ids is not None:
        unique_item_ids = list(dict.fromkeys(new_item_ids))
        if len(unique_item_ids) != len(new_item_ids):
            raise HTTPException(status_code=422, detail="Duplicate item IDs are not allowed")

        items = session.exec(select(Item).where(col(Item.id).in_(unique_item_ids))).all()
        found_ids = {item.id for item in items}
        missing = [item_id for item_id in unique_item_ids if item_id not in found_ids]
        if missing:
            raise HTTPException(status_code=404, detail=f"Item(s) not found: {missing}")
        deleted = [item.id for item in items if item.deleted_at is not None]
        if deleted:
            raise HTTPException(status_code=422, detail=f"Deleted item(s) cannot be assigned: {deleted}")

        # Replace the loaned items (safe: the loan has not started, nothing
        # returned). Reassigning the collection lets the delete-orphan cascade
        # remove the previous rows.
        db_loan.loaned_items = [
            LoanedItem(item_id=item_id)  # ty: ignore[missing-argument]
            for item_id in unique_item_ids
        ]

    db_loan.sqlmodel_update(update_data)
    session.add(db_loan)
    session.commit()

    reloaded = session.exec(select(Loan).where(Loan.id == loan_id).options(*_loan_load_options())).first()
    return reloaded  # ty: ignore[invalid-return-type]


@router.delete(
    "/{loan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Loan not found"}},
)
def delete_loan(
    session: SessionDep,
    _user: ClapDep,
    loan_id: Annotated[int, Path(ge=1)],
) -> None:
    db_loan = session.get(Loan, loan_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")

    # Deleting a loan that came from a request sends that request back to pending.
    if db_loan.request is not None:
        db_loan.request.status = RequestStatus.PENDING
        session.add(db_loan.request)

    session.delete(db_loan)
    session.commit()
