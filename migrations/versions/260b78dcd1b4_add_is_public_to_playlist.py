"""add is_public to playlist

Revision ID: 260b78dcd1b4
Revises: d800135c7435
Create Date: 2026-04-05 21:04:59.313614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '260b78dcd1b4'
down_revision = 'd800135c7435'
branch_labels = None
depends_on = None


def upgrade():
    pass  # is_public already added by d800135c7435


def downgrade():
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.drop_column('is_public')
