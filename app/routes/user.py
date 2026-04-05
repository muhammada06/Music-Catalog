import os
import requests
from flask import Blueprint, current_app, render_template, request, redirect, send_file, send_from_directory, url_for, abort, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Song, Playlist, linkPlaylistSong
from app import db
from datetime import datetime
from sqlalchemy import or_

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
    
        existing_email = User.query.filter_by(email=request.form['email'].strip()).first()
        if existing_email:
            flash("Email already registered")
            return redirect(url_for("auth.login"))
        
        new_user.set_email(request.form['email'].strip())

        db.session.add(new_user)
        db.session.flush()

        playlist = Playlist(name="Favorites", user_id=new_user.id)
        db.session.add(playlist)

        db.session.commit()
        flash("User created successfully. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@user.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('user.browse_playlists'))

@user.route('/playlist/view/<int:playlist_id>')
@login_required
def view_playlist(playlist_id):
    playlist = Playlist.query.filter((Playlist.id == playlist_id) & ((Playlist.user_id == current_user.id) | (Playlist.is_public == True))).first_or_404()

    songs = [
        {
            "id": link.song.id,
            "title": link.song.title,
            "artist": link.song.artist,
            "album": link.song.album,
            "genre": link.song.genre,
            "release_date": link.song.release_date.isoformat() if link.song.release_date else "",
            "audio_file": link.song.audio_file,
            "album_cover": link.song.album_cover,
            "online_source": link.song.online_source,
            "preview_url": link.song.preview_url
        } for link in playlist.songs
    ]
    playlists_data = [{'id': p.id, 'name': p.name} for p in current_user.playlists]
    return render_template("display_playlist.html", playlist=playlist, songs=songs, playlists=playlists_data)

@user.route('/toggle_playlist_privacy/<int:playlist_id>', methods=['POST'])
@login_required
def toggle_playlist_privacy(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()

    playlist.is_public = not playlist.is_public
    db.session.commit()

    return jsonify({'is_public': playlist.is_public})

@user.route('/playlists')
@login_required
def browse_playlists():
    songs_data = [
        {
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "album": s.album,
            "genre": s.genre,
            "release_date": s.release_date.isoformat() if s.release_date else "",
            "audio_file": s.audio_file,
            "album_cover": s.album_cover,
            "online_source": s.online_source,
            "preview_url": s.preview_url
        } for s in Song.query.all()
    ]
    playlists = Playlist.query.filter(or_(Playlist.user_id == current_user.id, Playlist.is_public == True)).all()

    playlists_data = [{'id': p.id, 'name': p.name, 'owner': p.user_id == current_user.id} for p in playlists]
    return render_template("display_playlist.html", songs=songs_data, playlists=playlists_data)

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
            return redirect(url_for("user.browse_playlists"))

        link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)

        db.session.add(link)
        db.session.commit()

        flash(f"The song {song.title} has been added to your {playlist.name}!", "success")

    return redirect(url_for("user.browse_playlists"))

@user.route('/add_to_playlist_ajax/<int:song_id>', methods=['POST'])
@login_required
def add_to_playlist_ajax(song_id):
    playlist_id = (request.json or {}).get('playlist_id')
    if not playlist_id:
        return jsonify({'error': 'No playlist selected'}), 400
    playlist = Playlist.query.filter_by(id=int(playlist_id), user_id=current_user.id).first_or_404()
    song = Song.query.get_or_404(song_id)
    if not linkPlaylistSong.query.filter_by(playlist_id=playlist.id, song_id=song.id).first():
        db.session.add(linkPlaylistSong(playlist_id=playlist.id, song_id=song.id))
        db.session.commit()
    return jsonify({'added': True, 'playlist': playlist.name})


@user.route('/rename_playlist/<int:playlist_id>', methods=['POST'])
@login_required
def rename_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()
    if playlist.name == 'Favorites':
        return jsonify({'error': 'Cannot rename Favorites'}), 403
    new_name = (request.json or {}).get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400
    existing = Playlist.query.filter_by(name=new_name, user_id=current_user.id).first()
    if existing and existing.id != playlist_id:
        return jsonify({'error': 'A playlist with that name already exists'}), 409
    playlist.name = new_name
    db.session.commit()
    return jsonify({'name': playlist.name})


@user.route('/delete_playlist/<int:playlist_id>', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()
    if playlist.name == 'Favorites':
        return jsonify({'error': 'Cannot delete Favorites'}), 403
    linkPlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'deleted': True})


@user.route('/toggle_favorite/<int:song_id>', methods=['POST'])
@login_required
def toggle_favorite(song_id):
    song = Song.query.get_or_404(song_id)
    fav = Playlist.query.filter_by(name='Favorites', user_id=current_user.id).first()
    if not fav:
        fav = Playlist(name='Favorites', user_id=current_user.id)
        db.session.add(fav)
        db.session.flush()

    link = linkPlaylistSong.query.filter_by(playlist_id=fav.id, song_id=song.id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        return jsonify({'in_favorites': False})
    else:
        db.session.add(linkPlaylistSong(playlist_id=fav.id, song_id=song.id))
        db.session.commit()
        return jsonify({'in_favorites': True})
    
@user.route('/is_favorite/<int:song_id>')
@login_required
def is_favorite(song_id):
    fav = Playlist.query.filter_by(name='Favorites', user_id=current_user.id).first()
    
    if not fav:
        return jsonify({'is_favorite': False})

    exists = linkPlaylistSong.query.filter_by(
        playlist_id=fav.id,
        song_id=song_id
    ).first() is not None

    return jsonify({'is_favorite': exists})


@user.route('/create_playlist', methods=["GET", "POST"])
@login_required
def create_playlist():
    if request.method == 'POST':
        playlist_name = request.form['playlist_name'].strip()
        existing_playlist = Playlist.query.filter_by(name=playlist_name, user_id=current_user.id).first()
        is_public = request.form.get('is_public') == 'on'

        if existing_playlist:
            flash("A playlist with that name already exists", "error")
            return redirect(url_for("user.browse_playlists"))
        
        playlist = Playlist(name=playlist_name, user_id=current_user.id, is_public=is_public)
    
        db.session.add(playlist)
        db.session.commit()

        flash("Your playlist has been successfully created, you may now add songs to it!", "success")

        return redirect(url_for("user.browse_playlists"))
    return render_template("create_playlist.html")

@user.route('/playlist/<int:playlist_id>')
@login_required
def get_playlist_songs(playlist_id):
    playlist = Playlist.query.filter((Playlist.id == playlist_id) & ((Playlist.user_id == current_user.id) | (Playlist.is_public == True))).first_or_404()
    
    songs = [
        {
            "id": link.song.id,
            "title": link.song.title,
            "artist": link.song.artist,
            "album": link.song.album,
            "genre": link.song.genre,
            "release_date": link.song.release_date.isoformat() if link.song.release_date else "",
            "audio_file": link.song.audio_file,
            "album_cover": link.song.album_cover,
            "online_source": link.song.online_source,
            "preview_url": link.song.preview_url
        } for link in playlist.songs
    ]
    return jsonify(songs)


@user.route('/play/<int:song_id>')
@login_required
def play(song_id):
    song = Song.query.get_or_404(song_id)
    folder_path = os.path.abspath(os.path.join('instance', 'demo_song'))

    return send_from_directory(folder_path, song.audio_file)

@user.route('/preview/stream/<int:song_id>')
@login_required
def stream_preview(song_id):
    song = Song.query.get_or_404(song_id)
    
    if not song.preview_url:
        abort(404)

    try:
        r = requests.get(song.preview_url, stream=True, timeout=10)
        r.raise_for_status()

        from flask import Response
        def generate():
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

        return Response(
            generate(),
            content_type=r.headers.get('Content-Type', 'audio/mpeg'),
            headers={
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'no-cache'
            }
        )
    except Exception as e:
        print("Stream error:", e)
        abort(502)

@user.route('/preview/<int:song_id>')
@login_required
def get_preview(song_id):
    song = Song.query.get_or_404(song_id)
    preview = None

    #return cached values if already stored
    if song.preview_url and song.deezer_track_id:
        return jsonify({"preview": song.preview_url, "deezer_id": song.deezer_track_id})

    try:
        query = f"{song.title} {song.artist}"
        url = f"https://api.deezer.com/search?q={query}"
        res = requests.get(url, timeout=3).json()

        if res.get("data"):
            for track in res["data"]:
                if song.artist.lower() in track["artist"]["name"].lower():
                    preview = track.get("preview")
                    deezer_id = track.get("id")
                    song.preview_url = preview
                    song.deezer_track_id = deezer_id
                    db.session.commit()
                    return jsonify({"preview": preview, "deezer_id": deezer_id})
    except Exception as e:
        print("Deezer error:", e)

    return jsonify({"preview": None, "deezer_id": None})