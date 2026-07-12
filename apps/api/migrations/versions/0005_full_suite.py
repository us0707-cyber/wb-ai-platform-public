"""Add analytics, pricing, synchronization and autopilot fields.

Revision ID: 0005_full_suite
Revises: 0004_product_seo_fields
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0005_full_suite"
down_revision: Union[str, None] = "0004_product_seo_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("marketplace_stores", sa.Column("last_sync_at", sa.DateTime(), nullable=True))
    op.add_column("marketplace_stores", sa.Column("sync_status", sa.String(30), nullable=False, server_default="never"))
    op.add_column("marketplace_stores", sa.Column("sync_error", sa.Text(), nullable=False, server_default=""))
    op.add_column("marketplace_stores", sa.Column("products_synced", sa.Integer(), nullable=False, server_default="0"))
    for name, typ, default in [
        ("discount", sa.Float(), "0"), ("cost_price", sa.Float(), "0"),
        ("commission_percent", sa.Float(), "15"), ("logistics_cost", sa.Float(), "0"),
        ("ad_spend_30d", sa.Float(), "0"), ("orders_30d", sa.Integer(), "0"),
        ("sales_30d", sa.Integer(), "0"), ("returns_30d", sa.Integer(), "0"),
        ("revenue_30d", sa.Float(), "0"), ("profit_30d", sa.Float(), "0"),
        ("ctr", sa.Float(), "0"), ("conversion_rate", sa.Float(), "0"),
        ("competitor_avg_price", sa.Float(), "0"), ("recommended_price", sa.Float(), "0"),
    ]:
        op.add_column("products", sa.Column(name, typ, nullable=False, server_default=default))
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("kind", sa.String(80), nullable=False, index=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open", index=True),
        sa.Column("action_data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("recommendations")
    for name in ["recommended_price","competitor_avg_price","conversion_rate","ctr","profit_30d","revenue_30d","returns_30d","sales_30d","orders_30d","ad_spend_30d","logistics_cost","commission_percent","cost_price","discount"]:
        op.drop_column("products", name)
    for name in ["products_synced","sync_error","sync_status","last_sync_at"]:
        op.drop_column("marketplace_stores", name)
