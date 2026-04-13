"""empty message

Revision ID: cd41a9387e01
Revises: dbe46c607ad6
Create Date: 2026-03-30 02:08:15.131342

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'cd41a9387e01'
down_revision = 'dbe46c607ad6'
branch_labels = None
depends_on = None


def _has_column(table, column):
    bind = op.get_bind()
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in [c['name'] for c in inspector.get_columns(table)]


def upgrade():
    if not _has_column('song', 'deezer_track_id'):
        with op.batch_alter_table('song', schema=None) as batch_op:
            batch_op.add_column(sa.Column('deezer_track_id', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.drop_column('deezer_track_id')