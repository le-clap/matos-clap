"""seed initial data

Revision ID: 76a675d6627e
Revises: d1aeacb5ec2f
Create Date: 2026-05-25 20:40:34.065276

"""

import os
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "76a675d6627e"
down_revision: str | Sequence[str] | None = "d1aeacb5ec2f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    current_dir = os.path.dirname(__file__)
    sql_path = os.path.join(current_dir, "../../db/seed.sql")

    with open(sql_path) as file:
        sql_commands = file.read()

    # Grab the underlying raw DBAPI connection from SQLAlchemy
    connection = op.get_bind()
    raw_connection = connection.connection

    # Execute the entire file natively through the Postgres cursor
    with raw_connection.cursor() as cursor:
        cursor.execute(sql_commands)


def downgrade() -> None:
    """Downgrade schema."""
    pass
