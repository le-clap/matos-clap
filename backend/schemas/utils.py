from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Common pagination parameters for list endpoints."""

    limit: int = Field(50, gt=0, le=100, description="Maximum number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    limit: int
    offset: int
