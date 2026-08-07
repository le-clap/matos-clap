from fastapi import Query
from pydantic import BaseModel


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
