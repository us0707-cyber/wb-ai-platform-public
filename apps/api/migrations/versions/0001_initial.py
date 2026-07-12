"""Initial schema.

Revision ID: 0001_initial
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "marketplace_stores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("marketplace", sa.String(50), nullable=False, server_default="wildberries"),
        sa.Column("api_token", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("owner_id", "name", name="uq_owner_store_name"),
    )
    op.create_index("ix_marketplace_stores_owner_id", "marketplace_stores", ["owner_id"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("store_id", sa.Integer(), sa.ForeignKey("marketplace_stores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nm_id", sa.Integer(), nullable=True),
        sa.Column("vendor_code", sa.String(120), nullable=False, server_default=""),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.String(200), nullable=False, server_default=""),
        sa.Column("brand", sa.String(200), nullable=False, server_default=""),
        sa.Column("price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reviews_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("seo_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_products_store_id", "products", ["store_id"])
    op.create_index("ix_products_nm_id", "products", ["nm_id"])

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_type", sa.String(80), nullable=False),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.Column("output_data", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_agent_runs_user_id", "agent_runs", ["user_id"])
    op.create_index("ix_agent_runs_agent_type", "agent_runs", ["agent_type"])


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("products")
    op.drop_table("marketplace_stores")
    op.drop_table("users")
