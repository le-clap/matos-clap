import time
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

# --- Reference Tables ---

class Condition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # New, Good, Degraded
    description: str | None = None

    # FastAPI "Shortcuts"
    items: List["Items"] = Relationship(back_populates="condition")


class Availability(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # Available, On Loan, Maintenance, Retired
    description: str | None = None

    items: List["Items"] = Relationship(back_populates="availability")


class Categories(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    catalogs: List["Catalog"] = Relationship(back_populates="category")


class Access(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # Unauthenticated/User/Clap/Manager/Admin
    description: str | None = None

    users: List["Users"] = Relationship(back_populates="access")


# --- Users ---

class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    last_name: str
    first_name: str
    email: str = Field(unique=True, index=True)
    access_id: int = Field(foreign_key="access.id")

    access: Access = Relationship(back_populates="users")
    requests: List["Requests"] = Relationship(back_populates="borrower")
    # Using sa_relationship_kwargs for multiple paths to the same table
    loans_as_borrower: List["Loans"] = Relationship(
        back_populates="borrower",
        sa_relationship_kwargs={"foreign_keys": "Loans.borrower_id"}
    )
    loans_as_assignee: List["Loans"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Loans.assignee_id"}
    )


# --- Inventory ---

class Catalog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    label: str
    description: str | None = None
    category_id: int = Field(foreign_key="categories.id")
    image_path: str | None = "pictures/default_picture.png"

    category: Categories = Relationship(back_populates="catalogs")
    items: List["Items"] = Relationship(back_populates="catalog")
    requested_in: List["Requested_items"] = Relationship(back_populates="catalog")


class Items(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # Internal ID (ex: CAM-01)
    catalog_id: int = Field(foreign_key="catalog.id")
    deposit: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    condition_id: int = Field(foreign_key="condition.id")
    availability_id: int = Field(foreign_key="availability.id")
    last_availability_update: datetime
    deleted: bool = Field(default=False)

    catalog: Catalog = Relationship(back_populates="items")
    condition: Condition = Relationship(back_populates="items")
    availability: Availability = Relationship(back_populates="items")
    loaned_in: List["Loaned_items"] = Relationship(back_populates="item")


# --- Request Flow ---

class Requests(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="users.id")
    phone_number: str
    start_date: datetime
    end_date: datetime
    reasons: str | None = None
    creation_date: datetime = Field(default_factory=datetime.now(timezone.utc))
    processed: bool = Field(default=False)

    borrower: Users = Relationship(back_populates="requests")
    items: List["Requested_items"] = Relationship(back_populates="request")
    loan: Loans | None = Relationship(back_populates="request")


class Requested_items(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="requests.id")
    catalog_id: int = Field(foreign_key="catalog.id")
    quantity: int = Field(default=1)

    request: Requests = Relationship(back_populates="items")
    catalog: Catalog = Relationship(back_populates="requested_in")


# --- Loan Flow ---

class Loans(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="users.id")
    assignee_id: int = Field(foreign_key="users.id")
    start_date: datetime
    end_date: datetime
    total_deposit: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    real_start_date: datetime | None = None
    real_return_date: datetime | None = None
    Retained_deposit: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    request_id: int | None = Field(default=None, foreign_key="requests.id")
    comments: str | None = None

    borrower: Users = Relationship(
        back_populates="loans_as_borrower",
        sa_relationship_kwargs={"foreign_keys": "[Loans.borrower_id]"}
    )
    assignee: Users = Relationship(
        back_populates="loans_as_assignee",
        sa_relationship_kwargs={"foreign_keys": "[Loans.assignee_id]"}
    )
    request: Requests | None = Relationship(back_populates="loan")
    items: List["Loaned_items"] = Relationship(back_populates="loan")


class Loaned_items(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    loan_id: int = Field(foreign_key="loans.id")
    item_id: int = Field(foreign_key="items.id")
    condition_on_return_id: int = Field(foreign_key="condition.id")

    loan: Loans = Relationship(back_populates="items")
    item: Items = Relationship(back_populates="loaned_in")