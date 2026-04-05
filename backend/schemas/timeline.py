from datetime import datetime

from pydantic import BaseModel

from models.enums import LoanStatus
from schemas.items import ItemBrief
from schemas.users import UserBrief


class LoanTimelineEntry(BaseModel):
    """A loan entry for calendar/timeline display."""

    loan_id: int
    borrower: UserBrief
    assignee: UserBrief
    start_date: datetime
    end_date: datetime
    actual_start_date: datetime | None = None
    actual_return_date: datetime | None = None
    status: LoanStatus
    items: list[ItemBrief]


class LoanTimelineResponse(BaseModel):
    """Response for loans timeline query."""

    start_date: datetime
    end_date: datetime
    loans: list[LoanTimelineEntry]
