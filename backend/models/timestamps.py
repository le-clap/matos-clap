from datetime import UTC, datetime

from pydantic import AwareDatetime
from sqlalchemy import func
from sqlmodel import Field, SQLModel


class TimestampSQLModel(SQLModel):
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"server_default": func.now()},
    )

    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


class SoftDeleteTimestampSQLModel(TimestampSQLModel):
    deleted_at: AwareDatetime | None = Field(default=None, index=True)
