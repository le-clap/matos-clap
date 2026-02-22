from datetime import datetime

from pydantic import BaseModel

from schemas.condition import ConditionPublic
from schemas.item import ItemBrief


class LoanedItemPost(BaseModel):
    item_id: int


class LoanedItemPatch(BaseModel):
    return_condition_id: int | None = None


class LoanedItemPublic(BaseModel):
    id: int
    item: ItemBrief
    return_condition: ConditionPublic | None = None


class LoanPost(BaseModel):
    borrower_id: int
    assignee_id: int
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int = 0
    request_id: int | None = None
    comments: str | None = None
    loaned_items: list[LoanedItemPost]


class LoanPatch(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    total_deposit_cents: int | None = None
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    retained_deposit_cents: int | None = None
    comments: str | None = None


class LoanPublic(BaseModel):
    id: int
    borrower_id: int
    assignee_id: int
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    retained_deposit_cents: int | None = None
    request_id: int | None = None
    comments: str | None = None
    loaned_items: list[LoanedItemPublic]
