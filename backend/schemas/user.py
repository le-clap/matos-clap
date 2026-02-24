from pydantic import BaseModel, EmailStr

from models.models import AccessLevel


class UserBrief(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    access_level: AccessLevel


class UserPost(BaseModel):
    username: str
    name: str
    email: EmailStr
    access_level: AccessLevel = AccessLevel.USER


class UserPatch(BaseModel):
    username: str | None = None
    name: str | None = None
    email: EmailStr | None = None
    access_level: AccessLevel | None = None


class UserPublic(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    access_level: AccessLevel
