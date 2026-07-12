"""Add user roles and audit log.

Revision ID: 0006_roles_and_audit
Revises: 0005_full_suite
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_roles_and_audit"
down_revision: Union[str, None] = "0005_full_suite"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="admin"))
    op.create_index("ix_users_role", "users", ["role"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_username", sa.String(100), nullable=False, server_default="system"),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False, server_default=""),
        sa.Column("entity_id", sa.String(100), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
        sa.Column("request_id", sa.String(64), nullable=False, server_default=""),
        sa.Column("ip_address", sa.String(64), nullable=False, server_default=""),
        sa.Column("details", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for column in ["user_id", "actor_username", "action", "entity_type", "status", "request_id", "created_at"]:
        op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
