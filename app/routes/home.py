from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.models import Song, Playlist
from app import db

homePage = Blueprint('home', __name__)

def _song_to_dict(s):
    if s.album_cover and s.album_cover.startswith('http'):
        cover = s.album_cover
    elif s.album_cover:
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

@homePage.route("/")
def home():
    songs = Song.query.order_by(Song.id).all()
    songs_data = [_song_to_dict(s) for s in songs]
    total = len(songs_data)

    favorite_ids = []
    if current_user.is_authenticated:
        fav = Playlist.query.filter_by(name='Favorites', user_id=current_user.id).first()
        if fav:
            favorite_ids = [link.song_id for link in fav.songs]

    return render_template("home.html", songs_data=songs_data, total=total, favorite_ids=favorite_ids)


@homePage.route("/songs-api")
def songs_api():
    page = request.args.get('page', 1, type=int)
    per_page = max(4, min(request.args.get('per_page', 32, type=int), 200))
    pagination = Song.query.order_by(Song.id).paginate(page=page, per_page=per_page, error_out=False)
    songs = [_song_to_dict(s) for s in pagination.items]
    return jsonify({'songs': songs, 'has_more': pagination.has_next, 'total': pagination.total})
