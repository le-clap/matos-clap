from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from models.enums import Availability
from schemas.catalogs import CatalogBrief
from schemas.users import UserBrief


class RequestedCatalogPost(BaseModel):
    catalog_id: int
    quantity: int = 1


class RequestedCatalogPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    catalog_id: int
    catalog: CatalogBrief
    quantity: int


class RequestPost(BaseModel):
    borrower_id: int
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    requested_catalogs: list[RequestedCatalogPost]

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class RequestPatch(BaseModel):
    phone_number: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    reason: str | None = None
    processed: bool | None = None


class RequestPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    borrower: UserBrief
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    created_at: datetime
    processed: bool
    requested_catalogs: list[RequestedCatalogPublic]


class RequestRecommendationItem(BaseModel):
    item_id: int
    item_name: str
    availability: Availability
    has_date_conflict: bool
    warning: str | None = None


class RequestedCatalogRecommendation(BaseModel):
    requested_catalog_id: int
    catalog: CatalogBrief
    requested_quantity: int
    recommended_item_ids: list[int]
    candidate_items: list[RequestRecommendationItem]
    warnings: list[str] = Field(default_factory=list)


class RequestRecommendationsResponse(BaseModel):
    request_id: int
    start_date: datetime
    end_date: datetime
    recommendations: list[RequestedCatalogRecommendation]
