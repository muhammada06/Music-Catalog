from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.models import Song, Playlist
from app import db

homePage = Blueprint('home', __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _song_to_dict(s):
    """Serialize a Song ORM object to a plain dictionary for JSON responses.

    Album cover URLs are handled in three cases:
      - External URL (starts with 'http') → used as-is.
      - Local filename                     → routed through /admin/cover/<filename>.
      - No cover set                       → None.
    """
    if s.album_cover and s.album_cover.startswith('http'):
        cover = s.album_cover
    elif s.album_cover:
        # Local covers are served by the admin blueprint
        cover = f'/admin/cover/{s.album_cover}'
    else:
        cover = None

    return {
        'id': s.id,
        'title': s.title,
        'artist': s.artist,
        'genre': s.genre or '',
        'year': s.release_date.year if s.release_date else None,
        'cover': cover,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@homePage.route("/")
def home():
    """Render the main homepage / song catalog.

    Passes the full song list to the template as JSON-serializable data so the
    front-end JS can render cards without an extra API round-trip on first load.
    For authenticated non-admin users, also injects their playlists and the IDs
    of songs they have favorited so the UI can pre-highlight them.
    """
    songs = Song.query.order_by(Song.id).all()
    songs_data = [_song_to_dict(s) for s in songs]
    total = len(songs_data)

    favorite_ids = []
    playlists_data = []
    if current_user.is_authenticated:
        # Load the user's Favorites playlist to pre-mark favorited songs
        fav = Playlist.query.filter_by(name='Favorites', user_id=current_user.id).first()
        if fav:
            favorite_ids = [link.song_id for link in fav.songs]
        # Admins don't have personal playlists in the catalog view
        if not current_user.is_admin:
            playlists_data = [{'id': p.id, 'name': p.name} for p in current_user.playlists]

    return render_template(
        "home.html",
        songs_data=songs_data,
        total=total,
        favorite_ids=favorite_ids,
        playlists_data=playlists_data,
    )


@homePage.route("/songs-api")
def songs_api():
    """Return a paginated JSON list of songs for infinite-scroll / lazy loading.

    Query params:
      page     (int, default 1)  – page number.
      per_page (int, default 32) – results per page, clamped to [4, 200].

    Response JSON:
      { songs: [...], has_more: bool, total: int }
    """
    page = request.args.get('page', 1, type=int)
    # Clamp per_page to a safe range to prevent excessively large queries
    per_page = max(4, min(request.args.get('per_page', 32, type=int), 200))
    pagination = Song.query.order_by(Song.id).paginate(page=page, per_page=per_page, error_out=False)
    songs = [_song_to_dict(s) for s in pagination.items]
    return jsonify({'songs': songs, 'has_more': pagination.has_next, 'total': pagination.total})
