from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from models.enums import Condition
from schemas.items import ItemBrief
from schemas.users import UserBrief


class LoanedItemPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    item: ItemBrief
    actual_return_date: datetime | None = None
    return_condition: Condition | None = None


class LoanPost(BaseModel):
    borrower_id: int
    assignee_id: int | None = None
    start_date: datetime
    end_date: datetime
    total_deposit_cents: int = Field(default=0, ge=0)
    request_id: int | None = None
    comments: str | None = None
    item_ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class LoanPatch(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    total_deposit_cents: int | None = Field(default=None, ge=0)
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    retained_deposit_cents: int | None = Field(default=None, ge=0)
    comments: str | None = None


class LoanPostWarning(BaseModel):
    code: str
    message: str
    item_id: int | None = None


class LoanPostResponse(BaseModel):
    loan: LoanPublic
    warnings: list[LoanPostWarning]


class LoanReturnItemCondition(BaseModel):
    item_id: int
    return_condition: Condition


class LoanPartialReturnItem(BaseModel):
    item_id: int
    return_condition: Condition | None = None


class LoanPartialReturnPost(BaseModel):
    items: list[LoanPartialReturnItem] = Field(min_length=1)


class LoanReturnPost(BaseModel):
    retained_deposit_cents: int = Field(ge=0)
    item_return_conditions: list[LoanReturnItemCondition] = Field(default_factory=list)
    comments: str | None = None


class LoanPublic(BaseModel):
    model_config = {"from_attributes": True}

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
