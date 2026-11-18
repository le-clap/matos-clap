from pydantic import BaseModel, ConfigDict

from schemas.categories import CategoryPublic
from schemas.utils import NonNull


class CatalogBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    image_path: str | None = None


class CatalogPost(BaseModel):
    name: str
    description: str | None = None
    category_id: int


class CatalogPatch(BaseModel):
    name: NonNull[str] = None
    description: str | None = None
    category_id: NonNull[int] = None


class CatalogImagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_path: str
    position: int


class CatalogImageOrder(BaseModel):
    image_ids: list[int]


class CatalogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    category: CategoryPublic
    image_path: str | None = None
    images: list[CatalogImagePublic] = []
