import secrets
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, Enum, Text
from sqlmodel import Field, Relationship, SQLModel

from models.enums import AccessLevel, Availability, Condition
from models.timestamps import TimestampSQLModel

# --- User ---


class User(TimestampSQLModel, table=True):
    """Represents a user of the system, who can be a borrower or an assignee."""

    __tablename__ = "matos_user"  # "user" is a reserved keyword in PostgreSQL

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, unique=True, index=True)
    access_level: AccessLevel = Field(
        default=AccessLevel.USER,
        sa_column=Column(Enum(AccessLevel, name="access_level", native_enum=False), nullable=False),
    )

    sessions: list[UserSession] = Relationship(back_populates="user")
    requests: list[Request] = Relationship(back_populates="borrower")
    loans_as_borrower: list[Loan] = Relationship(
        back_populates="borrower", sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    loans_as_assignee: list[Loan] = Relationship(
        back_populates="assignee", sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )


class UserSession(TimestampSQLModel, table=True):
    """Represents an active login session."""

    __tablename__ = "user_session"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(max_length=64, unique=True, index=True, default_factory=lambda: secrets.token_urlsafe(32))
    user_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="CASCADE")
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, index=True))

    user: User = Relationship(back_populates="sessions")


# --- Inventory ---


class Category(TimestampSQLModel, table=True):
    """Represents a category of catalogs in the inventory."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, sa_type=Text)

    catalogs: list[Catalog] = Relationship(back_populates="category")


class Catalog(TimestampSQLModel, table=True):
    """Represents a catalog of items in the inventory, linked to a category."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, sa_type=Text)
    category_id: int = Field(foreign_key="category.id", index=True, ondelete="RESTRICT")
    image_path: str | None = Field(default=None, max_length=255)

    category: Category = Relationship(back_populates="catalogs")
    items: list[Item] = Relationship(back_populates="catalog")
    requested_catalogs: list[RequestedCatalog] = Relationship(back_populates="catalog")


class Item(TimestampSQLModel, table=True):
    """Represents a physical item in the inventory, linked to a catalog."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    catalog_id: int = Field(foreign_key="catalog.id", index=True, ondelete="RESTRICT")
    condition: Condition = Field(
        default=Condition.NEW,
        sa_column=Column(Enum(Condition, name="condition", native_enum=False), nullable=False),
    )
    availability: Availability = Field(
        default=Availability.AVAILABLE,
        sa_column=Column(Enum(Availability, name="availability", native_enum=False), nullable=False),
    )
    deposit_cents: int = Field(default=0, ge=0)
    deleted_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))

    catalog: Catalog = Relationship(back_populates="items")
    loaned_items: list[LoanedItem] = Relationship(back_populates="item")


# --- Request Flow ---


class Request(TimestampSQLModel, table=True):
    """Represents a borrower's request to loan items, which can be processed into a loan."""

    id: int | None = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="RESTRICT")
    phone_number: str = Field(max_length=20)
    start_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    end_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    reason: str | None = Field(default=None, max_length=255)
    processed: bool = False

    borrower: User = Relationship(back_populates="requests")
    requested_catalogs: list[RequestedCatalog] = Relationship(back_populates="request")
    loan: Optional["Loan"] = Relationship(back_populates="request")  # noqa UP045


class RequestedCatalog(SQLModel, table=True):
    """Represents a specific catalog and quantity requested within a borrower's request."""

    __tablename__ = "requested_catalog"

    id: int | None = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="request.id", index=True, ondelete="CASCADE")
    catalog_id: int = Field(foreign_key="catalog.id", index=True, ondelete="RESTRICT")
    quantity: int = Field(default=1)

    request: Request = Relationship(back_populates="requested_catalogs")
    catalog: Catalog = Relationship(back_populates="requested_catalogs")


# --- Loan Flow ---


class Loan(TimestampSQLModel, table=True):
    """Represents an actual loan of items to a borrower, for example processed from a request."""

    id: int | None = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="RESTRICT")
    assignee_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="RESTRICT")
    start_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    end_date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    total_deposit_cents: int = Field(default=0, ge=0)
    actual_start_date: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    actual_return_date: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    retained_deposit_cents: int | None = Field(default=None, ge=0)
    request_id: int | None = Field(default=None, foreign_key="request.id", index=True, ondelete="SET NULL")
    comments: str | None = Field(default=None, sa_type=Text)

    borrower: User = Relationship(
        back_populates="loans_as_borrower", sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    assignee: User = Relationship(
        back_populates="loans_as_assignee", sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )
    request: Request | None = Relationship(back_populates="loan")
    loaned_items: list[LoanedItem] = Relationship(back_populates="loan")


class LoanedItem(SQLModel, table=True):
    """Represents a specific item that was loaned within a loan."""

    __tablename__ = "loaned_item"

    id: int | None = Field(default=None, primary_key=True)
    loan_id: int = Field(foreign_key="loan.id", index=True, ondelete="CASCADE")
    item_id: int = Field(foreign_key="item.id", index=True, ondelete="RESTRICT")
    actual_return_date: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    return_condition: Condition | None = Field(
        default=None,
        sa_column=Column(Enum(Condition, name="condition", native_enum=False), nullable=True),
    )

    loan: Loan = Relationship(back_populates="loaned_items")
    item: Item = Relationship(back_populates="loaned_items")
