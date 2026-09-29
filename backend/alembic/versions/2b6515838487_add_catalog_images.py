"""Add catalog images table

Revision ID: 2b6515838487
Revises: d1aeacb5ec2f
Create Date: 2026-09-20 16:49:13.412671

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b6515838487"
down_revision: str | Sequence[str] | None = "d1aeacb5ec2f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "catalog_image",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("catalog_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["catalog_id"], ["catalog.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("catalog_image", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_catalog_image_catalog_id"), ["catalog_id"], unique=False)

    # Data migration: carry each catalog's existing single image over as its cover (position 0).
    catalog = sa.table("catalog", sa.column("id", sa.Integer()), sa.column("image_path", sa.String()))
    catalog_image = sa.table(
        "catalog_image",
        sa.column("catalog_id", sa.Integer()),
        sa.column("image_path", sa.String()),
        sa.column("position", sa.Integer()),
    )
    conn = op.get_bind()
    for catalog_id, image_path in conn.execute(
        sa.select(catalog.c.id, catalog.c.image_path).where(catalog.c.image_path.is_not(None))
    ):
        conn.execute(catalog_image.insert().values(catalog_id=catalog_id, image_path=image_path, position=0))

    with op.batch_alter_table("catalog", schema=None) as batch_op:
        batch_op.drop_column("image_path")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("catalog", schema=None) as batch_op:
        batch_op.add_column(sa.Column("image_path", sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    # Data migration: carry each catalog's cover image (position 0) back onto the column.
    catalog = sa.table("catalog", sa.column("id", sa.Integer()), sa.column("image_path", sa.String()))
    catalog_image = sa.table(
        "catalog_image",
        sa.column("catalog_id", sa.Integer()),
        sa.column("image_path", sa.String()),
        sa.column("position", sa.Integer()),
    )
    conn = op.get_bind()
    for catalog_id, image_path in conn.execute(
        sa.select(catalog_image.c.catalog_id, catalog_image.c.image_path).where(catalog_image.c.position == 0)
    ):
        conn.execute(catalog.update().where(catalog.c.id == catalog_id).values(image_path=image_path))

    with op.batch_alter_table("catalog_image", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_catalog_image_catalog_id"))

    op.drop_table("catalog_image")
