import re
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from models.enums import Availability, RequestStatus
from schemas.catalogs import CatalogBrief
from schemas.users import UserBrief

# French phone number, optionally with +33 prefix and common separators.
_PHONE_RE = re.compile(r"^(?:\+33|0)[1-9]\d{8}$")


def normalize_phone_number(value: str) -> str:
    """Strip separators and validate a French phone number."""
    cleaned = re.sub(r"[\s.\-()]", "", value)

    if not _PHONE_RE.match(cleaned):
        raise ValueError("Numéro de téléphone invalide (format français attendu, ex. 06 12 34 56 78)")
    return "+33" + cleaned[1:] if cleaned.startswith("0") else cleaned


class RequestedCatalogPost(BaseModel):
    catalog_id: int
    quantity: int = 1


class RequestedCatalogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    catalog_id: int
    catalog: CatalogBrief
    quantity: int


class RequestPost(BaseModel):
    borrower_id: int
    phone_number: str
    start_date: AwareDatetime
    end_date: AwareDatetime
    reason: str | None = None
    requested_catalogs: list[RequestedCatalogPost]

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone_number(value)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class RequestPatch(BaseModel):
    phone_number: str | None = None
    start_date: AwareDatetime | None = None
    end_date: AwareDatetime | None = None
    reason: str | None = None
    status: RequestStatus | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_phone_number(value) if value is not None else None


class RequestPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    borrower: UserBrief
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    created_at: datetime
    processed: bool
    refused: bool
    status: RequestStatus
    loan_id: int | None = None
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
