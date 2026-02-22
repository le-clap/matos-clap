from pydantic import BaseModel


class AvailabilityPost(BaseModel):
    name: str
    description: str | None = None


class AvailabilityPublic(BaseModel):
    id: int
    name: str
    description: str | None = None


class AvailabilityPatch(BaseModel):
    name: str | None = None
    description: str | None = None
