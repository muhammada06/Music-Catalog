from flask import Blueprint, render_template
from sqlalchemy import func
from app.models import Song
from app import db

homePage = Blueprint('home', __name__)

@homePage.route("/")
def home():
    new_releases = (Song.query
        .filter(Song.release_date.isnot(None))
        .order_by(Song.release_date.desc())
        .limit(16).all())

    shuffle = Song.query.order_by(func.random()).limit(16).all()

    top_genres = (db.session.query(Song.genre, func.count(Song.id))
        .filter(Song.genre.isnot(None), Song.genre != '')
        .group_by(Song.genre)
        .order_by(func.count(Song.id).desc())
        .limit(4).all())

    genre_sections = [
        {'name': g, 'songs': Song.query.filter(Song.genre == g).limit(16).all()}
        for g, _ in top_genres
    ]

    total_songs = Song.query.count()
    return render_template("home.html",
        new_releases=new_releases,
        shuffle=shuffle,
        genre_sections=genre_sections,
        total_songs=total_songs)
