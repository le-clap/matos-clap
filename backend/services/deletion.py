"""Shared purge-or-archive deletion logic for the inventory hierarchy."""

from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped
from sqlmodel import Session, col, select

from models.models import Loan, LoanedItem
from models.timestamps import SoftDeleteTimestampSQLModel


def purge_or_archive[T: SoftDeleteTimestampSQLModel](session: Session, model: type[T], obj_id: int) -> bool:
    """Hard-delete the row; archive it (idempotently) if the DB refuses.

    Returns True if the row was purged, False if it was archived.
    """
    obj = session.get(model, obj_id)
    if obj is None:
        return False

    try:
        session.delete(obj)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()

    # The instance is expired after the rollback; re-fetch before mutating it.
    obj = session.get(model, obj_id)
    if obj is not None and obj.deleted_at is None:
        obj.deleted_at = datetime.now(UTC)
        session.add(obj)
        session.commit()
    return False


def has_live_children[T: SoftDeleteTimestampSQLModel](
    session: Session, model: type[T], parent_fk: Mapped[int], parent_id: int
) -> bool:
    """Whether any non-archived row of `model` still references `parent_id` via `parent_fk`."""
    live_child = select(parent_fk).where(parent_fk == parent_id, col(model.deleted_at).is_(None))
    return session.exec(select(live_child.exists())).one()


def item_has_open_loan(session: Session, item_id: int) -> bool:
    """Whether the item is part of a loan that hasn't been fully returned yet."""
    open_loaned_item = (
        select(LoanedItem.id)
        .join(Loan, col(LoanedItem.loan_id) == Loan.id)
        .where(
            LoanedItem.item_id == item_id,
            func.coalesce(LoanedItem.actual_return_date, Loan.actual_return_date).is_(None),
        )
    )
    return session.exec(select(open_loaned_item.exists())).one()
