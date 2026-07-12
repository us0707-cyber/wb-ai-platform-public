"""Add product catalog fields.

Revision ID: 0003_product_catalog_fields
Revises: 0002_store_connection_status
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_product_catalog_fields"
down_revision: Union[str, None] = "0002_store_connection_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"))
    op.add_column("products", sa.Column("image_url", sa.Text(), nullable=False, server_default=""))
    op.create_index("ix_products_status", "products", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_status", table_name="products")
    op.drop_column("products", "image_url")
    op.drop_column("products", "status")
