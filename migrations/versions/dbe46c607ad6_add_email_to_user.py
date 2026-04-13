"""add email to user

Revision ID: dbe46c607ad6
Revises: 63662c6f276f
Create Date: 2026-03-28 21:42:04.393169

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'dbe46c607ad6'
down_revision = '63662c6f276f'
branch_labels = None
depends_on = None


def _has_column(table, column):
    bind = op.get_bind()
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in [c['name'] for c in inspector.get_columns(table)]


def upgrade():
    if not _has_column('user', 'email'):
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=True))
            batch_op.create_unique_constraint('uq_user_email', ['email'])


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_email', type_='unique')
        batch_op.drop_column('email')