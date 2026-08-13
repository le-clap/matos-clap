import itertools
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from db.database import get_session
from main import app
from models.enums import AccessLevel, Availability, Condition
from models.models import Catalog, Category, Item, Loan, LoanedItem, User, UserSession

# ── Engine / session / client ─────────────────────────────────────────────────


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
        """SQLite ignores foreign keys unless explicitly told to enforce them."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()


# ── Helpers ────────────────────────────────────────────────────────────────────


def make_user(session: Session, level: AccessLevel, n: int) -> User:
    u = User(
        username=f"u{n}_{level}",
        name=f"User {n}",
        email=f"u{n}_{level}@centralelille.fr",
        access_level=level,
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def make_token(session: Session, user: User, *, expired: bool = False) -> str:
    delta = timedelta(days=-1 if expired else 30)
    us = UserSession(user_id=user.id, expires_at=datetime.now(UTC) + delta)
    session.add(us)
    session.commit()
    session.refresh(us)
    return us.token


# ── Factory fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def f_user(session):
    """Returns a callable: f_user(level) -> User."""
    c = itertools.count()
    return lambda level=AccessLevel.USER: make_user(session, level, next(c))


@pytest.fixture
def f_token(session):
    """Returns a callable: f_token(user, expired=False) -> token_str."""
    return lambda user, expired=False: make_token(session, user, expired=expired)


@pytest.fixture
def f_category(session):
    c = itertools.count()

    def _f(name: str | None = None) -> Category:
        n = next(c)
        cat = Category(name=name or f"Cat{n}")
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat

    return _f


@pytest.fixture
def f_catalog(session):
    c = itertools.count()

    def _f(category: Category, name: str | None = None) -> Catalog:
        n = next(c)
        cat = Catalog(name=name or f"Catalog{n}", category_id=category.id)
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat

    return _f


@pytest.fixture
def f_item(session):
    c = itertools.count()

    def _f(
        catalog: Catalog,
        availability: Availability = Availability.AVAILABLE,
        condition: Condition = Condition.GOOD,
        deposit_cents: int = 0,
    ) -> Item:
        n = next(c)
        item = Item(
            name=f"Item{n}",
            catalog_id=catalog.id,
            availability=availability,
            condition=condition,
            deposit_cents=deposit_cents,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    return _f


@pytest.fixture
def f_loan(session):
    """Returns a callable to create Loan + LoanedItem rows directly in the DB."""

    def _f(
        borrower: User,
        assignee: User,
        items: list[Item],
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        actual_start: datetime | None = None,
        actual_return: datetime | None = None,
        total_deposit_cents: int = 0,
    ) -> Loan:
        now = datetime.now(UTC)
        loan = Loan(
            borrower_id=borrower.id,
            assignee_id=assignee.id,
            start_date=start or now,
            end_date=end or now + timedelta(days=7),
            actual_start_date=actual_start,
            actual_return_date=actual_return,
            total_deposit_cents=total_deposit_cents,
        )
        session.add(loan)
        session.flush()
        for item in items:
            session.add(
                LoanedItem(
                    loan_id=loan.id,
                    item_id=item.id,
                    actual_return_date=actual_return,
                )
            )
        session.commit()
        session.refresh(loan)
        return loan

    return _f


# ── Commonly-used date helpers ────────────────────────────────────────────────


def dt(days_offset: int = 0) -> datetime:
    """Return a timezone-aware UTC datetime offset by `days_offset` from now."""
    return datetime.now(UTC) + timedelta(days=days_offset)


def iso(days_offset: int = 0) -> str:
    """Return an ISO 8601 UTC string offset by `days_offset`."""
    return dt(days_offset).isoformat()


def auth(token: str) -> dict[str, str]:
    """Return Bearer auth headers for a session token."""
    return {"Authorization": f"Bearer {token}"}
