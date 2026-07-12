"""Add AI engine cache.

Revision ID: 0007_ai_engine
Revises: 0006_roles_and_audit
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_ai_engine"
down_revision: Union[str, None] = "0006_roles_and_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cache_key", sa.String(64), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=True),
        sa.Column("task", sa.String(80), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False, server_default="local"),
        sa.Column("model", sa.String(120), nullable=False, server_default="deterministic-v1"),
        sa.Column("response_data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for column in ["cache_key", "user_id", "product_id", "task", "created_at"]:
        op.create_index(f"ix_ai_cache_{column}", "ai_cache", [column], unique=(column == "cache_key"))


def downgrade() -> None:
    op.drop_table("ai_cache")
