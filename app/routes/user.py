import os

from flask import Blueprint, current_app, render_template, request, redirect, send_file, send_from_directory, url_for, abort, flash
from flask_login import login_required, current_user
from app.models import User, Song, Playlist, linkPlaylistSong
from app import db
from datetime import datetime

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/get')
def get():
    return render_template('user_account.html')

@user.route('/creation', methods=["GET", "POST"])
def creation():
    if request.method == 'POST':
        new_user = User()

        username = request.form['username'].strip()
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("auth.login"))
        
        new_user.set_username(request.form['username'].strip())
        new_user.set_password(request.form['password'])
        new_user.set_email(request.form['email'].strip())
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@user.route('/dashboard')
@login_required
def dashboard():
    # Show all songs in the database for user-side view (read-only)
    songs = Song.query.all()
    playlists = current_user.playlists
    playlists_data = [{'id': p.id, 'name': p.name} for p in playlists]
    return render_template("user_dashboard.html", songs=songs, playlists=playlists_data)

@user.route('/add_to_playlist/<int:song_id>', methods=["POST"])
@login_required
def add_to_playlist(song_id):
    if request.method == 'POST':
        playlist_id = request.form['playlist_id']

        if playlist_id == "NEW":
            flash("You are being redirected to the playlist creation page!")
            return redirect(url_for("user.create_playlist"))
        
        playlist_id = int(playlist_id)
        playlist = Playlist.query.get_or_404(playlist_id)

        song = Song.query.get_or_404(song_id)
        song_in_playlist = linkPlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()

        if song_in_playlist:
            flash(f"{song.title} is already in the {playlist.name}!", "error")
            return redirect(url_for("user.dashboard"))

        link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)

        db.session.add(link)
        db.session.commit()

        flash(f"The song {song.title} has been added to your {playlist.name}!", "success")

    return redirect(url_for("user.dashboard"))

@user.route('/create_playlist', methods=["GET", "POST"])
@login_required
def create_playlist():
    if request.method == 'POST':
        playlist_name = request.form['playlist_name'].strip()
        existing_playlist = Playlist.query.filter_by(name=playlist_name, user_id=current_user.id).first()

        if existing_playlist:
            flash("A playlist with that name already exists", "error")
            return redirect(url_for("user.dashboard"))
        
        playlist = Playlist(name=playlist_name, user_id=current_user.id)
    
        db.session.add(playlist)
        db.session.commit()

        flash("Your playlist has been successfully created, you may now add songs to it!", "success")

        return redirect(url_for("user.dashboard"))
    return render_template("create_playlist.html")


@user.route('/play/<int:song_id>')
@login_required
def play(song_id):
    song = Song.query.get_or_404(song_id)
    folder_path = os.path.abspath(os.path.join('instance', 'demo_song'))

    return send_from_directory(folder_path, song.audio_file)