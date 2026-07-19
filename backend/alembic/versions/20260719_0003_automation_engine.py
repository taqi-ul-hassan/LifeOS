"""Add internal automation engine tables."""

from alembic import op
from app.automation import models

revision = "20260719_0003"
down_revision = "20260719_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in [
        models.AutomationRule.__table__,
        models.Workflow.__table__,
        models.WorkflowStep.__table__,
        models.Trigger.__table__,
        models.Condition.__table__,
        models.Action.__table__,
        models.ScheduledJob.__table__,
        models.Execution.__table__,
        models.ExecutionHistory.__table__,
        models.ExecutionLog.__table__,
        models.RetryQueue.__table__,
        models.AutomationMetric.__table__,
        models.AutomationNotification.__table__,
        models.AutomationAudit.__table__,
    ]:
        table.create(bind, checkfirst=True)


def downgrade() -> None:
    pass
