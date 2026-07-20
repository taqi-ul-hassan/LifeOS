"""Add indexes for user-scoped planning and reporting queries.

Revision ID: 20260720_0005
Revises: 20260720_0004
Create Date: 2026-07-20
"""

from alembic import op
import sqlalchemy as sa


revision = "20260720_0005"
down_revision = "20260720_0004"
branch_labels = None
depends_on = None


INDEXES = (
    ("ix_goals_user_status_target", "goals", ["user_id", "status", "target_date"]),
    ("ix_tasks_user_status_due", "tasks", ["user_id", "status", "due_at"]),
    ("ix_calendar_events_user_starts", "calendar_events", ["user_id", "starts_at"]),
    (
        "ix_health_metrics_user_type_measured",
        "health_metrics",
        ["user_id", "metric_type", "measured_at"],
    ),
    (
        "ix_financial_records_user_occurred",
        "financial_records",
        ["user_id", "occurred_on"],
    ),
)


def upgrade() -> None:
    # The first revision creates metadata wholesale, so a fresh database may
    # already contain these model-declared indexes.  Keep the migration safe
    # in both fresh and incrementally upgraded environments.
    inspector = sa.inspect(op.get_bind())
    for name, table, columns in INDEXES:
        existing = {index["name"] for index in inspector.get_indexes(table)}
        if name not in existing:
            op.create_index(name, table, columns)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    for name, table, _ in INDEXES:
        if name in {index["name"] for index in inspector.get_indexes(table)}:
            op.drop_index(name, table_name=table)
