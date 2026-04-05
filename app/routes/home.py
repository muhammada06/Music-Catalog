from flask import Blueprint, render_template, request, jsonify
from app.models import Song
from app import db

homePage = Blueprint('home', __name__)

@homePage.route("/")
def home():
    total = Song.query.count()
    return render_template("home.html", total=total)

@homePage.route("/songs-api")
def songs_api():
    page = request.args.get('page', 1, type=int)
    per_page = max(4, min(request.args.get('per_page', 32, type=int), 200))
    pagination = Song.query.order_by(Song.id).paginate(page=page, per_page=per_page, error_out=False)

    songs = []
    for s in pagination.items:
        if s.album_cover and s.album_cover.startswith('http'):
            cover = s.album_cover
        elif s.album_cover:
            cover = f'/admin/covers/{s.album_cover}'
        else:
            cover = None
        songs.append({'id': s.id, 'title': s.title, 'artist': s.artist, 'cover': cover})

    return jsonify({'songs': songs, 'has_more': pagination.has_next, 'total': pagination.total})
