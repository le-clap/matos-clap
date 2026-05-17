from pydantic import BaseModel

from schemas.categories import CategoryPublic


class CatalogBrief(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    image_path: str | None = None


class CatalogPost(BaseModel):
    name: str
    description: str | None = None
    category_id: int
    image_path: str | None = None


class CatalogPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    image_path: str | None = None


class CatalogPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: str | None = None
    category: CategoryPublic
    image_path: str | None = None
