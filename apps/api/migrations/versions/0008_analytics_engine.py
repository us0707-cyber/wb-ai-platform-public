"""Add analytics daily facts.

Revision ID: 0008_analytics_engine
Revises: 0007_ai_engine
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_analytics_engine"
down_revision: Union[str, None] = "0007_ai_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analytics_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sales", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("returns", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue", sa.Float(), nullable=False, server_default="0"),
        sa.Column("profit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("ad_spend", sa.Float(), nullable=False, server_default="0"),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("product_id", "day", name="uq_analytics_product_day"),
    )
    op.create_index("ix_analytics_daily_user_id", "analytics_daily", ["user_id"])
    op.create_index("ix_analytics_daily_product_id", "analytics_daily", ["product_id"])
    op.create_index("ix_analytics_daily_day", "analytics_daily", ["day"])
    op.create_index("ix_analytics_daily_user_day", "analytics_daily", ["user_id", "day"])


def downgrade() -> None:
    op.drop_table("analytics_daily")
