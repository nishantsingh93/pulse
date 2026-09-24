"""Initial Pulse POC schema.

Revision ID: 0001
Revises:
"""
from alembic import op
from pulse.db import Base
import pulse.models

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    Base.metadata.create_all(bind=op.get_bind())


def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
