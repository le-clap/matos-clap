from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
import uuid

# --- Reference Tables ---

class Condition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # New, Good, Degraded
    description: str | None = None

    item: List["Item"] = Relationship(back_populates="condition")


class Availability(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # Available, On Loan, Maintenance, Retired
    description: str | None = None

    item: List["Item"] = Relationship(back_populates="availability")


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    catalog: List["Catalog"] = Relationship(back_populates="category")


class Access(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # Unauthenticated/User/Clap/Manager/Admin
    description: str | None = None

    user: List["User"] = Relationship(back_populates="access")


# --- User ---

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    last_name: str
    first_name: str
    email: EmailStr = Field(unique=True, index=True)
    session_id: str | None = Field(default_factory=lambda: uuid.uuid4().hex)

    access_id: int = Field(foreign_key="access.id")

    access: Access = Relationship(back_populates="user")
    request: List["Request"] = Relationship(back_populates="borrower")
    # Using sa_relationship_kwargs for multiple paths to the same table
    loan_as_borrower: List["Loan"] = Relationship(
        back_populates="borrower",
        sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    loan_as_assignee: List["Loan"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )


# --- Inventory ---

class Catalog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    label: str
    description: str | None = None
    category_id: int = Field(foreign_key="category.id")
    image_path: str | None = "pictures/default_picture.png"

    category: Category = Relationship(back_populates="catalog")
    item: List["Item"] = Relationship(back_populates="catalog")
    requested_in: List["RequestedItem"] = Relationship(back_populates="catalog")


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str  # Internal ID (ex: CAM-01)
    catalog_id: int = Field(foreign_key="catalog.id")
    deposit: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    condition_id: int = Field(foreign_key="condition.id")
    availability_id: int = Field(foreign_key="availability.id")
    last_availability_update: datetime
    deleted: bool = Field(default=False)

    catalog: Catalog = Relationship(back_populates="item")
    condition: Condition = Relationship(back_populates="item")
    availability: Availability = Relationship(back_populates="item")
    loaned_in: List["LoanedItem"] = Relationship(back_populates="item")


# --- Request Flow ---

class Request(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    borrower_id: int = Field(foreign_key="user.id")
    phone_number: str
    start_date: datetime
    end_date: datetime
    reasons: str | None = None
    creation_date: datetime = Field(default_factory=datetime.now)
    processed: bool = Field(default=False)

    borrower: User = Relationship(back_populates="request")
    item: List["RequestedItem"] = Relationship(back_populates="request")
    loan: Optional["Loan"] = Relationship(back_populates="request")


class RequestedItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    request_id: int = Field(foreign_key="request.id")
    catalog_id: int = Field(foreign_key="catalog.id")
    quantity: int = Field(default=1)

    request: Request = Relationship(back_populates="item")
    catalog: Catalog = Relationship(back_populates="requested_in")


# --- Loan Flow ---

class Loan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    borrower_id: int = Field(foreign_key="user.id")
    assignee_id: int = Field(foreign_key="user.id")
    start_date: datetime
    end_date: datetime
    total_deposit: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    real_start_date: Optional[datetime]
    real_return_date: Optional[datetime]
    Retained_deposit: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    request_id: int | None = Field(default=None, foreign_key="request.id")
    comments: str | None = None

    borrower: User = Relationship(
        back_populates="loan_as_borrower",
        sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    assignee: User = Relationship(
        back_populates="loan_as_assignee",
        sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )
    request: Optional[Request] = Relationship(back_populates="loan")
    item: List["LoanedItem"] = Relationship(back_populates="loan")


class LoanedItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    loan_id: int = Field(foreign_key="loan.id")
    item_id: int = Field(foreign_key="item.id")
    condition_on_return_id: int = Field(foreign_key="condition.id")

    loan: Loan = Relationship(back_populates="item")
    item: Item = Relationship(back_populates="loaned_in")