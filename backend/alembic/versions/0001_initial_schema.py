"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "grocery_items",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), index=True, nullable=False),
        sa.Column("quantity", sa.String(), nullable=False),
        sa.Column("category", sa.String(), index=True, nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_consumed", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_table(
        "blacklisted_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("token", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("limit_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("spent_amount", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "month", "year", name="uq_budget_user_month_year"),
    )
    op.create_table(
        "shopping_items",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), index=True, nullable=False),
        sa.Column("quantity", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("is_purchased", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "alert_settings",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("days_before_expiry", sa.Integer(), server_default="3", nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("alert_settings")
    op.drop_table("shopping_items")
    op.drop_table("budgets")
    op.drop_table("blacklisted_tokens")
    op.drop_table("grocery_items")
    op.drop_table("users")
