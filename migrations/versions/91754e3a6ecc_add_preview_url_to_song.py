"""add preview_url to song

Revision ID: 91754e3a6ecc
Revises: cd41a9387e01
Create Date: 2026-04-04 22:20:58.855382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91754e3a6ecc'
down_revision = 'cd41a9387e01'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preview_url', sa.String(length=500), nullable=True))


def downgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.drop_column('preview_url')
