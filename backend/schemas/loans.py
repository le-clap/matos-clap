from datetime import datetime

from pydantic import BaseModel, model_validator

from models.enums import Condition
from schemas.items import ItemBrief
from schemas.users import UserBrief


class LoanedItemPost(BaseModel):
    item_id: int


class LoanedItemPatch(BaseModel):
    return_condition: Condition | None = None


class LoanedItemPublic(BaseModel):
    id: int
    item: ItemBrief
    return_condition: Condition | None = None


class LoanPost(BaseModel):
    borrower_id: int
    assignee_id: int
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int = 0
    request_id: int | None = None
    comments: str | None = None
    loaned_items: list[LoanedItemPost]

    @classmethod
    @model_validator(mode="after")
    def validate_dates(cls, data):
        if data.start_date >= data.end_date:
            raise ValueError("start_date must be before end_date")
        return data


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
    borrower: UserBrief
    assignee: UserBrief
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    retained_deposit_cents: int | None = None
    request_id: int | None = None
    comments: str | None = None
    loaned_items: list[LoanedItemPublic]
