from datetime import datetime

from pydantic import BaseModel

from schemas.catalog import CatalogBrief


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


class RequestPatch(BaseModel):
    phone_number: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    reason: str | None = None
    processed: bool | None = None


class RequestPublic(BaseModel):
    id: int
    borrower_id: int
    phone_number: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None
    creation_date: datetime
    processed: bool
    requested_catalogs: list[RequestedCatalogPublic]
