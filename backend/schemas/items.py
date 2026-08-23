from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import Availability, Condition, LoanStatus
from schemas.catalogs import CatalogPublic
from schemas.users import UserBrief


class ItemBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    catalog: CatalogPublic
    condition: Condition
    availability: Availability
    deposit_cents: int


class ItemAvailabilityResponse(BaseModel):
    available: list[ItemPublic]
    unavailable: list[ItemPublic]


class ItemHistoryEntry(BaseModel):
    """One stint of an item in a borrower's hands, derived from a loan."""

    loan_id: int
    borrower: UserBrief
    assignee: UserBrief
    start_date: datetime
    end_date: datetime
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    return_condition: Condition | None = None
    status: LoanStatus
