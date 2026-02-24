from datetime import datetime

from pydantic import BaseModel, model_validator

from schemas.catalogs import CatalogBrief
from schemas.users import UserBrief


class RequestedCatalogPost(BaseModel):
    catalog_id: int
    quantity: int = 1


class RequestedCatalogPublic(BaseModel):
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

    @classmethod
    @model_validator(mode="after")
    def validate_dates(cls, data):
        if data.start_date >= data.end_date:
            raise ValueError("start_date must be before end_date")
        return data


class RequestPatch(BaseModel):
    phone_number: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    reason: str | None = None
    processed: bool | None = None


class RequestPublic(BaseModel):
    id: int
    borrower: UserBrief
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    creation_date: datetime
    processed: bool
    requested_catalogs: list[RequestedCatalogPublic]
