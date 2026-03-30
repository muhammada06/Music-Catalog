from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    email      = db.Column(db.String(255), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    playlists = db.relationship('Playlist', backref='user', lazy=True)

    def set_username(self, plain_user_name):
        self.username = plain_user_name

    def set_password(self, plain_user_password):
        if not plain_user_password:
            raise ValueError("Password cannot be empty")
        self.password = generate_password_hash(plain_user_password)

    def set_email(self, plain_user_email):
        self.email = plain_user_email

    def set_is_admin(self):
        self.is_admin = True

    def check_password(self, plain_user_password):
        return check_password_hash(self.password, plain_user_password)
    
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    __table_args__ = (db.UniqueConstraint('user_id', 'name'),)

class linkPlaylistSong(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)

    playlist = db.relationship('Playlist', backref='songs')
    song = db.relationship('Song', backref='playlists')
    
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    genre = db.Column(db.String(100))
    release_date = db.Column(db.Date)
    audio_file = db.Column(db.String(255))
    album_cover = db.Column(db.String(255))
    online_source = db.Column(db.String(500))
    deezer_track_id = db.Column(db.Integer, nullable=True)
    preview_url = db.Column(db.String(500), nullable=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))