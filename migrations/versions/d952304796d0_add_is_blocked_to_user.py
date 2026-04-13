"""add is_blocked to user

Revision ID: d952304796d0
Revises: ebc9b33a02db
Create Date: 2026-04-05 09:03:19.490973

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'd952304796d0'
down_revision = 'ebc9b33a02db'
branch_labels = None
depends_on = None


def _has_column(table, column):
    bind = op.get_bind()
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in [c['name'] for c in inspector.get_columns(table)]


def upgrade():
    if not _has_column('user', 'is_blocked'):
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('is_blocked', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_blocked')