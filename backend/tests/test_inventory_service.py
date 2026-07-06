"""Unit tests for services.inventory.find_busy_item_ids."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session

from models.enums import AccessLevel, Availability, Condition
from models.models import Catalog, Category, Item, Loan, LoanedItem, User
from services.inventory import find_busy_item_ids

# ── Helpers ───────────────────────────────────────────────────────────────────


def _user(session: Session, n: int = 0) -> User:
    u = User(username=f"srv_u{n}", name=f"U{n}", email=f"srv{n}@test.com", access_level=AccessLevel.USER)
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def _item(session: Session, catalog: Catalog, n: int = 0) -> Item:
    item = Item(
        name=f"srv_item{n}", catalog_id=catalog.id, availability=Availability.AVAILABLE, condition=Condition.GOOD
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def _loan_for(
    session: Session,
    borrower: User,
    assignee: User,
    items: list[Item],
    start: datetime,
    end: datetime,
    actual_start: datetime | None = None,
    actual_return: datetime | None = None,
    item_actual_return: datetime | None = None,
) -> Loan:
    loan = Loan(
        borrower_id=borrower.id,
        assignee_id=assignee.id,
        start_date=start,
        end_date=end,
        actual_start_date=actual_start,
        actual_return_date=actual_return,
    )
    session.add(loan)
    session.flush()
    for item in items:
        session.add(LoanedItem(loan_id=loan.id, item_id=item.id, actual_return_date=item_actual_return))
    session.commit()
    session.refresh(loan)
    return loan


@pytest.fixture
def base(session, engine):
    """Provide borrower, assignee, category, catalog, and two items."""
    borrower = _user(session, 0)
    assignee = _user(session, 1)
    cat = Category(name="SvcCat")
    session.add(cat)
    session.commit()
    session.refresh(cat)
    catalog = Catalog(name="SvcCatalog", category_id=cat.id)
    session.add(catalog)
    session.commit()
    session.refresh(catalog)
    item_a = _item(session, catalog, 0)
    item_b = _item(session, catalog, 1)
    return borrower, assignee, item_a, item_b


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_empty_item_ids(session):
    now = datetime.now(UTC)
    result = find_busy_item_ids(session, [], now, now + timedelta(days=1))
    assert result == set()


def test_no_loans(session, base):
    _, _, item_a, item_b = base
    now = datetime.now(UTC)
    result = find_busy_item_ids(session, [item_a.id, item_b.id], now, now + timedelta(days=7))
    assert result == set()


def test_non_overlapping_loan_before_range(session, base):
    """Loan ends before the query start → not busy."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    # loan: [now-10, now-3]
    _loan_for(session, borrower, assignee, [item_a], now - timedelta(days=10), now - timedelta(days=3))
    # query: [now, now+7]
    result = find_busy_item_ids(session, [item_a.id], now, now + timedelta(days=7))
    assert result == set()


def test_non_overlapping_loan_after_range(session, base):
    """Loan starts after the query end → not busy."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    # loan: [now+10, now+17]
    _loan_for(session, borrower, assignee, [item_a], now + timedelta(days=10), now + timedelta(days=17))
    # query: [now, now+7]
    result = find_busy_item_ids(session, [item_a.id], now, now + timedelta(days=7))
    assert result == set()


def test_boundary_loan_end_equals_query_start(session, base):
    """Loan effective end == query start is NOT busy (strict > check)."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    query_start = now + timedelta(days=5)
    _loan_for(session, borrower, assignee, [item_a], now, query_start)
    result = find_busy_item_ids(session, [item_a.id], query_start, query_start + timedelta(days=3))
    assert result == set()


def test_boundary_loan_start_equals_query_end(session, base):
    """Loan effective start == query end is NOT busy (strict < check)."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    query_end = now + timedelta(days=5)
    _loan_for(session, borrower, assignee, [item_a], query_end, query_end + timedelta(days=3))
    result = find_busy_item_ids(session, [item_a.id], now, query_end)
    assert result == set()


def test_loan_fully_overlapping_range(session, base):
    """Loan spans the entire query range → busy."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    _loan_for(session, borrower, assignee, [item_a], now - timedelta(days=1), now + timedelta(days=10))
    result = find_busy_item_ids(session, [item_a.id], now, now + timedelta(days=7))
    assert item_a.id in result


def test_loan_partial_overlap_at_start(session, base):
    """Loan starts before and ends during the query range → busy."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    _loan_for(session, borrower, assignee, [item_a], now - timedelta(days=3), now + timedelta(days=3))
    result = find_busy_item_ids(session, [item_a.id], now, now + timedelta(days=7))
    assert item_a.id in result


def test_loan_partial_overlap_at_end(session, base):
    """Loan starts during and ends after the query range → busy."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    _loan_for(session, borrower, assignee, [item_a], now + timedelta(days=4), now + timedelta(days=10))
    result = find_busy_item_ids(session, [item_a.id], now, now + timedelta(days=7))
    assert item_a.id in result


def test_actual_start_date_shifts_effective_start(session, base):
    """actual_start_date replaces start_date in the overlap calculation."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    # Scheduled start was 3 days ago but actual start is tomorrow → should NOT overlap [now-2, now-1]
    _loan_for(
        session,
        borrower,
        assignee,
        [item_a],
        start=now - timedelta(days=3),
        end=now + timedelta(days=5),
        actual_start=now + timedelta(days=1),
    )
    result = find_busy_item_ids(session, [item_a.id], now - timedelta(days=2), now - timedelta(days=1))
    assert result == set()


def test_item_actual_return_date_shifts_effective_end(session, base):
    """LoanedItem.actual_return_date is used as effective end when set."""
    borrower, assignee, item_a, _ = base
    now = datetime.now(UTC)
    # Loan scheduled to end now+7, but item was actually returned yesterday
    _loan_for(
        session,
        borrower,
        assignee,
        [item_a],
        start=now - timedelta(days=3),
        end=now + timedelta(days=7),
        item_actual_return=now - timedelta(days=1),
    )
    # Query [now, now+5] should NOT see item as busy since it was returned yesterday
    result = find_busy_item_ids(session, [item_a.id], now, now + timedelta(days=5))
    assert result == set()


def test_multiple_items_only_some_busy(session, base):
    """Only overlapping items are in the returned set."""
    borrower, assignee, item_a, item_b = base
    now = datetime.now(UTC)
    # item_a: busy (overlaps)
    _loan_for(session, borrower, assignee, [item_a], now, now + timedelta(days=5))
    # item_b: no loan
    result = find_busy_item_ids(session, [item_a.id, item_b.id], now + timedelta(days=1), now + timedelta(days=3))
    assert item_a.id in result
    assert item_b.id not in result
