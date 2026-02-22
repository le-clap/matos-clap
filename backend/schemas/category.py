from pydantic import BaseModel


class CategoryPost(BaseModel):
    name: str
    description: str | None = None


class CategoryPatch(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryPublic(BaseModel):
    id: int
    name: str
    description: str | None = None
