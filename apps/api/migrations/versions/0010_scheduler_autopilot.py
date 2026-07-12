"""Add scheduler and autopilot rules.

Revision ID: 0010_scheduler_autopilot
Revises: 0009_job_engine
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_scheduler_autopilot"
down_revision = "0009_job_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("schedule_type", sa.String(length=20), nullable=False, server_default="interval"),
        sa.Column("interval_minutes", sa.Integer(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_schedules_user_id", "schedules", ["user_id"])
    op.create_index("ix_schedules_job_type", "schedules", ["job_type"])
    op.create_index("ix_schedules_schedule_type", "schedules", ["schedule_type"])
    op.create_index("ix_schedules_next_run_at", "schedules", ["next_run_at"])
    op.create_index("ix_schedules_enabled", "schedules", ["enabled"])

    op.create_table(
        "autopilot_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("rule_type", sa.String(length=40), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False, server_default="0"),
        sa.Column("action_type", sa.String(length=40), nullable=False, server_default="recommendation"),
        sa.Column("config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_autopilot_rules_user_id", "autopilot_rules", ["user_id"])
    op.create_index("ix_autopilot_rules_rule_type", "autopilot_rules", ["rule_type"])
    op.create_index("ix_autopilot_rules_enabled", "autopilot_rules", ["enabled"])

    op.add_column("jobs", sa.Column("source_schedule_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_jobs_source_schedule_id", "jobs", "schedules", ["source_schedule_id"], ["id"], ondelete="SET NULL"
    )
    op.create_index("ix_jobs_source_schedule_id", "jobs", ["source_schedule_id"])


def downgrade() -> None:
    op.drop_index("ix_jobs_source_schedule_id", table_name="jobs")
    op.drop_constraint("fk_jobs_source_schedule_id", "jobs", type_="foreignkey")
    op.drop_column("jobs", "source_schedule_id")
    op.drop_index("ix_autopilot_rules_enabled", table_name="autopilot_rules")
    op.drop_index("ix_autopilot_rules_rule_type", table_name="autopilot_rules")
    op.drop_index("ix_autopilot_rules_user_id", table_name="autopilot_rules")
    op.drop_table("autopilot_rules")
    op.drop_index("ix_schedules_enabled", table_name="schedules")
    op.drop_index("ix_schedules_next_run_at", table_name="schedules")
    op.drop_index("ix_schedules_schedule_type", table_name="schedules")
    op.drop_index("ix_schedules_job_type", table_name="schedules")
    op.drop_index("ix_schedules_user_id", table_name="schedules")
    op.drop_table("schedules")
