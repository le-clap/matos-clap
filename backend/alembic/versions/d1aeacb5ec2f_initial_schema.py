"""Initial Schema

Revision ID: d1aeacb5ec2f
Revises:
Create Date: 2026-03-01 13:11:36.290215

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1aeacb5ec2f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("category", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_category_deleted_at"), ["deleted_at"], unique=False)
    op.create_table(
        "matos_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "access_level",
            sa.Enum("USER", "CLAP", "MANAGER", "ADMIN", name="access_level", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("matos_user", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_matos_user_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_matos_user_username"), ["username"], unique=True)

    op.create_table(
        "catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("catalog", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_catalog_category_id"), ["category_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_catalog_deleted_at"), ["deleted_at"], unique=False)

    op.create_table(
        "request",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "REFUSED", "APPROVED", name="request_status", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["borrower_id"], ["matos_user.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("request", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_request_borrower_id"), ["borrower_id"], unique=False)

    op.create_table(
        "user_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["matos_user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("user_session", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_session_expires_at"), ["expires_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_session_token"), ["token"], unique=True)
        batch_op.create_index(batch_op.f("ix_user_session_user_id"), ["user_id"], unique=False)

    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("catalog_id", sa.Integer(), nullable=False),
        sa.Column(
            "condition",
            sa.Enum("NEW", "GOOD", "DEGRADED", name="condition", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "availability",
            sa.Enum("AVAILABLE", "MAINTENANCE", "RETIRED", name="availability", native_enum=False),
            nullable=False,
        ),
        sa.Column("deposit_cents", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["catalog_id"], ["catalog.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("item", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_item_catalog_id"), ["catalog_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_item_deleted_at"), ["deleted_at"], unique=False)

    op.create_table(
        "loan",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_deposit_cents", sa.Integer(), nullable=False),
        sa.Column("actual_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_return_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retained_deposit_cents", sa.Integer(), nullable=True),
        sa.Column("request_id", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assignee_id"], ["matos_user.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["borrower_id"], ["matos_user.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["request_id"], ["request.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("loan", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_loan_assignee_id"), ["assignee_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_loan_borrower_id"), ["borrower_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_loan_request_id"), ["request_id"], unique=False)

    op.create_table(
        "requested_catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("catalog_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["catalog_id"], ["catalog.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["request_id"], ["request.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("requested_catalog", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_requested_catalog_catalog_id"), ["catalog_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_requested_catalog_request_id"), ["request_id"], unique=False)

    op.create_table(
        "loaned_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("loan_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("actual_return_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "return_condition",
            sa.Enum("NEW", "GOOD", "DEGRADED", name="condition", native_enum=False),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["loan_id"], ["loan.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("loaned_item", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_loaned_item_item_id"), ["item_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_loaned_item_loan_id"), ["loan_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("loaned_item", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_loaned_item_loan_id"))
        batch_op.drop_index(batch_op.f("ix_loaned_item_item_id"))

    op.drop_table("loaned_item")
    with op.batch_alter_table("requested_catalog", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_requested_catalog_request_id"))
        batch_op.drop_index(batch_op.f("ix_requested_catalog_catalog_id"))

    op.drop_table("requested_catalog")
    with op.batch_alter_table("loan", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_loan_request_id"))
        batch_op.drop_index(batch_op.f("ix_loan_borrower_id"))
        batch_op.drop_index(batch_op.f("ix_loan_assignee_id"))

    op.drop_table("loan")
    with op.batch_alter_table("item", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_item_deleted_at"))
        batch_op.drop_index(batch_op.f("ix_item_catalog_id"))

    op.drop_table("item")
    with op.batch_alter_table("user_session", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_session_user_id"))
        batch_op.drop_index(batch_op.f("ix_user_session_token"))
        batch_op.drop_index(batch_op.f("ix_user_session_expires_at"))

    op.drop_table("user_session")
    with op.batch_alter_table("request", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_request_borrower_id"))

    op.drop_table("request")
    with op.batch_alter_table("catalog", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_catalog_deleted_at"))
        batch_op.drop_index(batch_op.f("ix_catalog_category_id"))

    op.drop_table("catalog")
    with op.batch_alter_table("matos_user", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_matos_user_username"))
        batch_op.drop_index(batch_op.f("ix_matos_user_email"))

    op.drop_table("matos_user")
    with op.batch_alter_table("category", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_category_deleted_at"))

    op.drop_table("category")
