"""Add secure integration platform tables."""

from alembic import op
from app.integrations import models

revision = "20260720_0004"
down_revision = "20260719_0003"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    for table in [
        models.IntegrationConnection.__table__,
        models.EncryptedCredential.__table__,
        models.WebhookDelivery.__table__,
        models.SyncRecord.__table__,
        models.IntegrationAudit.__table__,
    ]:
        table.create(bind, checkfirst=True)


def downgrade():
    pass
