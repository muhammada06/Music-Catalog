from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

#This is the object user where all users table is modelled after in database
class User(UserMixin, db.Model):
    #User atributes
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    email      = db.Column(db.String(255), unique=True, nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    playlists = db.relationship('Playlist', backref='user', lazy=True)

    #Method to set the user name in database
    def set_username(self, plain_user_name):
        self.username = plain_user_name

    #Method to set the user password in database
    def set_password(self, plain_user_password):
        #Check if password is empty
        if not plain_user_password:
            raise ValueError("Password cannot be empty")
        self.password = generate_password_hash(plain_user_password)#Hashes the password before storing it in the database

    #Method to set the user email
    def set_email(self, plain_user_email):
        self.email = plain_user_email

    #Method to set the user as an admin
    def set_is_admin(self):
        self.is_admin = True

    #Method to check inputed password with current users password
    def check_password(self, plain_user_password):
        return check_password_hash(self.password, plain_user_password)

#This is the object Playlist where all Playlist table is modelled after in database   
class Playlist(db.Model):
    #Playlist atributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_public = db.Column(db.Boolean, default=False)

    #Makes sure that the current user can not have a playlist with the same name
    __table_args__ = (db.UniqueConstraint('user_id', 'name'),)

#This is the object linkPlaylistSong where all songs are linked to the playlist in the database 
class linkPlaylistSong(db.Model):
    #linkPlaylistSong atributes
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)

    #Links a song and playlist together in the database
    playlist = db.relationship('Playlist', backref='songs')
    song = db.relationship('Song', backref='playlists')

#This is the object Song where all songs table is modelled after in database
class Song(db.Model):
    #Song atributes
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
    
#This logs users in while using the software
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))