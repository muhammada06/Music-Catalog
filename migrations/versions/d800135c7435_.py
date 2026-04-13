"""empty message

Revision ID: d800135c7435
Revises: d952304796d0
Create Date: 2026-04-05 15:36:34.232011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd800135c7435'
down_revision = 'd952304796d0'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'is_public' column to allow playlists to be marked as public or private
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_public', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # Remove 'is_public' column from playlist table
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.drop_column('is_public')

    # ### end Alembic commands ###
