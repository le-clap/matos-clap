from pydantic import AwareDatetime, BaseModel, ConfigDict

from models.enums import Availability, Condition, LoanStatus
from schemas.catalogs import CatalogBrief
from schemas.users import UserBrief
from schemas.utils import NonNull


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
    name: NonNull[str] = None
    catalog_id: NonNull[int] = None
    condition: NonNull[Condition] = None
    availability: NonNull[Availability] = None
    deposit_cents: NonNull[int] = None


class ItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    catalog: CatalogBrief
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
    start_date: AwareDatetime
    end_date: AwareDatetime
    actual_start_date: AwareDatetime | None = None
    actual_return_date: AwareDatetime | None = None
    return_condition: Condition | None = None
    status: LoanStatus
