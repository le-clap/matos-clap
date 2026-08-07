from pydantic import BaseModel, ConfigDict


class CategoryPost(BaseModel):
    name: str
    description: str | None = None


class CategoryPatch(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
