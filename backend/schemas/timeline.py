from pydantic import AwareDatetime, BaseModel

from models.enums import LoanStatus
from schemas.items import ItemBrief
from schemas.users import UserBrief


class LoanTimelineEntry(BaseModel):
    """A loan entry for calendar/timeline display."""

    loan_id: int
    borrower: UserBrief
    assignee: UserBrief
    start_date: AwareDatetime
    end_date: AwareDatetime
    actual_start_date: AwareDatetime | None = None
    actual_return_date: AwareDatetime | None = None
    status: LoanStatus
    items: list[ItemBrief]


class LoanTimelineResponse(BaseModel):
    """Response for loans timeline query."""

    start_date: AwareDatetime
    end_date: AwareDatetime
    loans: list[LoanTimelineEntry]
