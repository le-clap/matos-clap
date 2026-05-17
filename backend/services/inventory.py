"""Shared inventory utilities for querying items and their availability."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from models.models import Catalog, Item, Loan, LoanedItem


def item_load_options():
    """SQLAlchemy load options for eager-loading item relationships."""
    return [
        joinedload(Item.catalog).joinedload(Catalog.category),  # ty: ignore[invalid-argument-type]
    ]


def find_busy_item_ids(
    session: Session,
    item_ids: list[int],
    start_date: datetime,
    end_date: datetime,
) -> set[int]:
    """Find item IDs that have overlapping loans in the given date range.

    An item is "busy" if it has an active loan that overlaps [start_date, end_date].
    The overlap considers:
    - Effective start < end_date (loan starts before our range ends)
    - Effective end  > start_date (loan ends after our range starts)
    """
    if not item_ids:
        return set()

    busy_stmt = (
        select(LoanedItem.item_id)
        .join(Loan, LoanedItem.loan_id == Loan.id)  # ty: ignore[invalid-argument-type]
        .where(
            LoanedItem.item_id.in_(item_ids),  # ty: ignore[unresolved-attribute]
            func.coalesce(
                Loan.actual_start_date,
                Loan.start_date,
            )
            < end_date,
            func.coalesce(
                LoanedItem.actual_return_date,
                Loan.actual_return_date,
                Loan.end_date,
            )
            > start_date,
        )
    )
    return set(session.exec(busy_stmt).all())
