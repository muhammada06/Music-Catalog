"""empty message

Revision ID: cd41a9387e01
Revises: dbe46c607ad6
Create Date: 2026-03-30 02:08:15.131342

"""
from alembic import op
import sqlalchemy as sa, inspect


# revision identifiers, used by Alembic.
revision = 'cd41a9387e01'
down_revision = 'dbe46c607ad6'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deezer_track_id', sa.Integer(), nullable=True))

def downgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.drop_column('deezer_track_id')
