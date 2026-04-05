from pydantic import BaseModel


class CategoryPost(BaseModel):
    name: str
    description: str | None = None


class CategoryPatch(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: str | None = None
