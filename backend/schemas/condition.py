from pydantic import BaseModel


class ConditionPost(BaseModel):
    name: str
    description: str | None = None


class ConditionPatch(BaseModel):
    name: str | None = None
    description: str | None = None


class ConditionPublic(BaseModel):
    id: int
    name: str
    description: str | None = None
