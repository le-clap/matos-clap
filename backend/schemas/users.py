from pydantic import BaseModel, EmailStr

from models.models import AccessLevel


class UserBrief(BaseModel):
    id: int
    username: str
    name: str
    access_level: AccessLevel


class UserPatch(BaseModel):
    access_level: AccessLevel


class UserPublic(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    access_level: AccessLevel
