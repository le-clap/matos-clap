from datetime import datetime

from pydantic import BaseModel

from schemas.availability import AvailabilityPublic
from schemas.catalog import CatalogPublic
from schemas.condition import ConditionPublic


class ItemBrief(BaseModel):
    id: int
    name: str


class ItemPost(BaseModel):
    name: str
    catalog_id: int
    deposit_cents: int = 0
    condition_id: int
    availability_id: int


class ItemPatch(BaseModel):
    name: str | None = None
    catalog_id: int | None = None
    deposit_cents: int | None = None
    condition_id: int | None = None
    availability_id: int | None = None


class ItemPublic(BaseModel):
    id: int
    name: str
    catalog_id: int
    catalog: CatalogPublic
    deposit_cents: int
    condition_id: int
    condition: ConditionPublic
    availability_id: int
    availability: AvailabilityPublic
    availability_update_date: datetime
    deleted: bool
