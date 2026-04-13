"""empty message

Revision ID: d800135c7435
Revises: d952304796d0
Create Date: 2026-04-05 15:36:34.232011

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'd800135c7435'
down_revision = 'd952304796d0'
branch_labels = None
depends_on = None


def _has_column(table, column):
    bind = op.get_bind()
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in [c['name'] for c in inspector.get_columns(table)]


def upgrade():
    if not _has_column('playlist', 'is_public'):
        with op.batch_alter_table('playlist', schema=None) as batch_op:
            batch_op.add_column(sa.Column('is_public', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.drop_column('is_public')
