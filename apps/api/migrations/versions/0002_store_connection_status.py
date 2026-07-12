"""Add store connection status fields.

Revision ID: 0002_store_connection_status
Revises: 0001_initial
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_store_connection_status"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("marketplace_stores", sa.Column("connection_status", sa.String(30), nullable=False, server_default="not_checked"))
    op.add_column("marketplace_stores", sa.Column("last_checked_at", sa.DateTime(), nullable=True))
    op.add_column("marketplace_stores", sa.Column("last_error", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("marketplace_stores", "last_error")
    op.drop_column("marketplace_stores", "last_checked_at")
    op.drop_column("marketplace_stores", "connection_status")
