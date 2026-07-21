from pydantic import BaseModel, ConfigDict, EmailStr

from models.models import AccessLevel


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    access_level: AccessLevel


class UserPatch(BaseModel):
    access_level: AccessLevel


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    email: EmailStr
    access_level: AccessLevel
