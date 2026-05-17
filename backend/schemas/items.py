from datetime import datetime

from pydantic import BaseModel

from models.enums import Availability, Condition, LoanStatus
from schemas.catalogs import CatalogPublic


class ItemBrief(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str


class ItemPost(BaseModel):
    name: str
    catalog_id: int
    condition: Condition
    availability: Availability = Availability.AVAILABLE
    deposit_cents: int = 0


class ItemPatch(BaseModel):
    name: str | None = None
    catalog_id: int | None = None
    condition: Condition | None = None
    availability: Availability | None = None
    deposit_cents: int | None = None


class ItemPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    catalog: CatalogPublic
    condition: Condition
    availability: Availability
    deposit_cents: int
    deleted_at: datetime | None = None


class ItemAvailabilityResponse(BaseModel):
    available: list[ItemPublic]
    unavailable: list[ItemPublic]


class LoanedItemWithLoan(BaseModel):
    """An item that is currently loaned out, with loan details."""

    item_id: int
    item_name: str
    catalog_name: str
    loan_id: int
    borrower_name: str
    loan_start_date: datetime
    loan_end_date: datetime
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    status: LoanStatus


class LoanedItemsResponse(BaseModel):
    """Response for querying items that are loaned out during a date range."""

    start_date: datetime
    end_date: datetime
    loaned_items: list[LoanedItemWithLoan]
