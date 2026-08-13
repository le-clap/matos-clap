from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlmodel import Field, SQLModel


class TimestampSQLModel(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_type=DateTime(timezone=True),  # ty: ignore[invalid-argument-type]
        sa_column_kwargs={"server_default": func.now()},
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_type=DateTime(timezone=True),  # ty: ignore[invalid-argument-type]
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


class SoftDeleteTimestampSQLModel(TimestampSQLModel):
    deleted_at: datetime | None = Field(
        default=None,
        nullable=True,
        index=True,
        sa_type=DateTime(timezone=True),  # ty: ignore[invalid-argument-type]
    )
