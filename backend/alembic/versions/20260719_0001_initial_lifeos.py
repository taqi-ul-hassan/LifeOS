"""Initial LifeOS relational data model.

Revision ID: 20260719_0001
Revises:
Create Date: 2026-07-19
"""
from alembic import op
from app.db import Base
import app.models  # noqa: F401

revision = "20260719_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    Base.metadata.create_all(op.get_bind())

def downgrade() -> None:
    Base.metadata.drop_all(op.get_bind())
