"""merge heads

Revision ID: ebc9b33a02db
Revises: 5becc3c7c0b2, 91754e3a6ecc
Create Date: 2026-04-05 09:03:16.857985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebc9b33a02db'
down_revision = ('5becc3c7c0b2', '91754e3a6ecc')
branch_labels = None
depends_on = None


def upgrade():
    # Merge migration: combines multiple revision branches into a single history
    pass


def downgrade():
    # No downgrade logic required for merge migrations
    pass
