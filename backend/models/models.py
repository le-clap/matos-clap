from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
import uuid

# --- Reference Tables ---

class Condition(SQLModel, table=True):
    """
    Represents the condition of an item in the inventory. Examples include: New, Good, Degraded.
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    items: list["Item"] = Relationship(back_populates="condition")


class Availability(SQLModel, table=True):
    """
    Represents the availability status of an item. Examples include: Available, On Loan, Maintenance, Retired.
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    items: list["Item"] = Relationship(back_populates="availability")


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    catalogs: list["Catalog"] = Relationship(back_populates="category")


class Access(SQLModel, table=True):
    """
    Represents the access level of a user. Examples include: Unauthenticated, User, Clap, Manager, Admin.
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    users: list["User"] = Relationship(back_populates="access")


# --- User ---

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(unique=True, index=True)
    name: str
    email: EmailStr = Field(unique=True, index=True)
    access_id: int = Field(foreign_key="access.id")

    session_id: str | None = Field(default_factory=lambda: uuid.uuid4().hex)

    access: Access = Relationship(back_populates="users")
    requests: list["Request"] = Relationship(back_populates="borrower")
    loans_as_borrower: list["Loan"] = Relationship(
        back_populates="borrower",
        sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    loans_as_assignee: list["Loan"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )


# --- Inventory ---

class Catalog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    category_id: int = Field(foreign_key="category.id")
    image_path: str | None = None

    category: Category = Relationship(back_populates="catalogs")
    items: list["Item"] = Relationship(back_populates="catalog")
    requested_catalogs: list["RequestedCatalog"] = Relationship(back_populates="catalog")


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str  # Internal ID (ex: CAM-01)
    catalog_id: int = Field(foreign_key="catalog.id")
    deposit_cents: int = Field(default=0, ge=0)
    condition_id: int = Field(foreign_key="condition.id")
    availability_id: int = Field(foreign_key="availability.id")
    availability_update_date: datetime
    deleted: bool = Field(default=False)

    catalog: Catalog = Relationship(back_populates="items")
    condition: Condition = Relationship(back_populates="items")
    availability: Availability = Relationship(back_populates="items")
    loaned_items: list["LoanedItem"] = Relationship(back_populates="item")


# --- Request Flow ---

class Request(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    borrower_id: int = Field(foreign_key="user.id")
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    creation_date: datetime = Field(default_factory=datetime.now)
    processed: bool = Field(default=False)

    borrower: User = Relationship(back_populates="requests")
    requested_catalogs: list["RequestedCatalog"] = Relationship(back_populates="request")
    loan: "Loan | None" = Relationship(back_populates="request")


class RequestedCatalog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    request_id: int = Field(foreign_key="request.id")
    catalog_id: int = Field(foreign_key="catalog.id")
    quantity: int = Field(default=1)

    request: Request = Relationship(back_populates="requested_catalogs")
    catalog: Catalog = Relationship(back_populates="requested_catalogs")


# --- Loan Flow ---

class Loan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    borrower_id: int = Field(foreign_key="user.id")
    assignee_id: int = Field(foreign_key="user.id")
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int = Field(default=0, ge=0)
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    retained_deposit_cents: int | None = Field(default=None, ge=0)
    request_id: int | None = Field(default=None, foreign_key="request.id")
    comments: str | None = None

    borrower: User = Relationship(
        back_populates="loans_as_borrower",
        sa_relationship_kwargs={"foreign_keys": "Loan.borrower_id"}
    )
    assignee: User = Relationship(
        back_populates="loans_as_assignee",
        sa_relationship_kwargs={"foreign_keys": "Loan.assignee_id"}
    )
    request: Request | None = Relationship(back_populates="loan")
    loaned_items: list["LoanedItem"] = Relationship(back_populates="loan")


class LoanedItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    loan_id: int = Field(foreign_key="loan.id")
    item_id: int = Field(foreign_key="item.id")
    return_condition_id: int | None = Field(default=None, foreign_key="condition.id")

    loan: Loan = Relationship(back_populates="loaned_items")
    item: Item = Relationship(back_populates="loaned_items")
    return_condition: Condition | None = Relationship()