from pydantic import BaseModel


class AvailabilityPost(BaseModel):
    name: str
    description: str


class AvailabilityPublic(BaseModel):
    id: int
    name: str
    description: str


class AvailabilityPatch(BaseModel):
    name: str | None
    description: str | None
