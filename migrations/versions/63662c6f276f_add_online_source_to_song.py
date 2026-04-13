
from alembic import op
import sqlalchemy as sa

revision = '63662c6f276f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), nullable=False),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('is_blocked', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    op.create_table('song',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('artist', sa.String(200), nullable=False),
        sa.Column('album', sa.String(200), nullable=True),
        sa.Column('genre', sa.String(100), nullable=True),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('audio_file', sa.String(255), nullable=True),
        sa.Column('album_cover', sa.String(255), nullable=True),
        sa.Column('online_source', sa.String(500), nullable=True),
        sa.Column('deezer_track_id', sa.Integer(), nullable=True),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('playlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name')
    )

    op.create_table('link_playlist_song',
        sa.Column('playlist_id', sa.Integer(), sa.ForeignKey('playlist.id'), nullable=False),
        sa.Column('song_id', sa.Integer(), sa.ForeignKey('song.id'), nullable=False),
        sa.PrimaryKeyConstraint('playlist_id', 'song_id')
    )


def downgrade():
    op.drop_table('link_playlist_song')
    op.drop_table('playlist')
    op.drop_table('song')
    op.drop_table('user')