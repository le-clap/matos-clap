from typing import Annotated, TypeVar

from fastapi import Query
from pydantic import BaseModel, BeforeValidator
from pydantic.json_schema import SkipJsonSchema

T = TypeVar("T")


def _reject_null(value):
    if value is None:
        raise ValueError("cannot be null")
    return value


# PATCH field for a NOT NULL column (JSON Merge Patch, RFC 7396): it may be
# omitted (default None + exclude_unset), but an explicit null is a 422.
# Runs before other constraints (ge, min_length...) so they never see None.
NonNull = Annotated[T | SkipJsonSchema[None], BeforeValidator(_reject_null)]


class PaginationParams(BaseModel):
    """Common pagination parameters for list endpoints."""

    limit: int = Query(50, gt=0, le=100, description="Maximum number of items to return")
    page: int = Query(0, ge=0, description="Page number")
    search: str | None = Query(None, description="Search term")

    def offset(self) -> int:
        """Calculate offset from page number."""
        return self.page * self.limit


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    limit: int
    page: int
    search: str | None
