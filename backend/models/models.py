import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from models.enums import AccessLevel, Availability, Condition

# --- User ---


class User(SQLModel, table=True):
    """Represents a user of the system, who can be a borrower or an assignee."""

    __tablename__ = "matos_user"  # "user" is a reserved keyword in PostgreSQL

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    name: str
    email: EmailStr = Field(unique=True, index=True)
    access_level: AccessLevel = AccessLevel.USER

    session_id: str | None = Field(default_factory=lambda: uuid.uuid4().hex)

    requests: list[Request] = Relationship(back_populates="borrower")
    loans_as_borrower: list[Loan] = Relationship(
        back_populates="borrower", sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    loans_as_assignee: list[Loan] = Relationship(
        back_populates="assignee", sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )


# --- Inventory ---


class Category(SQLModel, table=True):
    """Represents a category of catalogs in the inventory."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    catalogs: list[Catalog] = Relationship(back_populates="category")


class Catalog(SQLModel, table=True):
    """Represents a catalog of items in the inventory, linked to a category."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    category_id: int = Field(foreign_key="category.id", index=True, ondelete="RESTRICT")
    image_path: str | None = None

    category: Category = Relationship(back_populates="catalogs")
    items: list[Item] = Relationship(back_populates="catalog")
    requested_catalogs: list[RequestedCatalog] = Relationship(back_populates="catalog")


class Item(SQLModel, table=True):
    """Represents a physical item in the inventory, linked to a catalog."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    catalog_id: int = Field(foreign_key="catalog.id", index=True, ondelete="RESTRICT")
    condition: Condition = Condition.NEW
    availability: Availability = Availability.AVAILABLE
    deposit_cents: int = Field(default=0, ge=0)
    deleted: bool = Field(default=False)

    catalog: Catalog = Relationship(back_populates="items")
    loaned_items: list[LoanedItem] = Relationship(back_populates="item")


# --- Request Flow ---


class Request(SQLModel, table=True):
    """Represents a borrower's request to loan items, which can be processed into a loan."""

    id: int | None = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="RESTRICT")
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    creation_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    processed: bool = Field(default=False)

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


class Loan(SQLModel, table=True):
    """Represents an actual loan of items to a borrower, for example processed from a request."""

    id: int | None = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="RESTRICT")
    assignee_id: int = Field(foreign_key="matos_user.id", index=True, ondelete="RESTRICT")
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int = Field(default=0, ge=0)
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    retained_deposit_cents: int | None = Field(default=None, ge=0)
    request_id: int | None = Field(default=None, foreign_key="request.id", index=True, ondelete="SET NULL")
    comments: str | None = None

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
    return_condition: Condition | None = None

    loan: Loan = Relationship(back_populates="loaned_items")
    item: Item = Relationship(back_populates="loaned_items")
