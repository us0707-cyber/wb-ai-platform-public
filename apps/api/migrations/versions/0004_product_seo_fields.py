"""Add generated SEO fields to products.

Revision ID: 0004_product_seo_fields
Revises: 0003_product_catalog_fields
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_product_seo_fields"
down_revision: Union[str, None] = "0003_product_catalog_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("seo_title", sa.String(length=500), nullable=False, server_default=""))
    op.add_column("products", sa.Column("seo_description", sa.Text(), nullable=False, server_default=""))
    op.add_column("products", sa.Column("seo_recommendations", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))
    op.add_column("products", sa.Column("seo_updated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "seo_updated_at")
    op.drop_column("products", "seo_recommendations")
    op.drop_column("products", "seo_description")
    op.drop_column("products", "seo_title")
