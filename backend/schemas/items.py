from pydantic import BaseModel

from models.enums import Availability, Condition
from schemas.catalogs import CatalogPublic


class ItemBrief(BaseModel):
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
    id: int
    name: str
    catalog: CatalogPublic
    condition: Condition
    availability: Availability
    deposit_cents: int
    deleted: bool


class ItemAvailabilityResponse(BaseModel):
    available: list[ItemPublic]
    unavailable: list[ItemPublic]
