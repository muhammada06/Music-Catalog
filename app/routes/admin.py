from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, send_from_directory
from flask_login import login_required, current_user
from app.models import Song, User
from app import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os

admin = Blueprint('admin', __name__, url_prefix='/admin')

AUDIO_DIR = os.path.join("instance", "demo_song")
COVER_DIR = os.path.join("instance", "album_covers")

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin.route('/get')
def get():
    return render_template('admin_account.html')

@admin.route('/creation', methods=["GET", "POST"])
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
        new_user.set_is_admin()
        db.session.add(new_user)
        db.session.commit()
        flash("Admin account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))

@admin.route('/dashboard')
@login_required
def dashboard():
    admin_required()
    songs = Song.query.all()
    return render_template('admin_dashboard.html', songs=songs)

@admin.route('/add', methods=['GET', 'POST'])
@login_required
def add_song():
    admin_required()

    if request.method == 'POST':
        release_date_str = request.form.get('release_date')
        release_date = None
        if release_date_str:
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()

        audio_filename = None
        file = request.files.get('audio')
        if file and file.filename:
            audio_filename = secure_filename(file.filename)
            os.makedirs(AUDIO_DIR, exist_ok=True)
            file.save(os.path.join(AUDIO_DIR, audio_filename))

        cover_filename = None
        cover = request.files.get('album_cover')
        if cover and cover.filename:
            cover_filename = secure_filename(cover.filename)
            os.makedirs(COVER_DIR, exist_ok=True)
            cover.save(os.path.join(COVER_DIR, cover_filename))

        song = Song(
            title=request.form.get('title'),
            artist=request.form.get('artist'),
            album=request.form.get('album'),
            genre=request.form.get('genre'),
            release_date=release_date,
            audio_file=audio_filename,
            album_cover=cover_filename,
            user_id=current_user.id
        )

        db.session.add(song)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('add_song.html')


@admin.route('/cover/<filename>')
def serve_cover(filename):
    folder = os.path.abspath(COVER_DIR)
    return send_from_directory(folder, filename)


@admin.route('/delete/<int:song_id>', methods=['POST'])
@login_required
def delete_song(song_id):
    admin_required()
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin.route('/edit/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit_song(song_id):
    admin_required()
    song = Song.query.get_or_404(song_id)

    if request.method == 'POST':
        song.title = request.form.get('title')
        song.artist = request.form.get('artist')
        song.album = request.form.get('album')
        song.genre = request.form.get('genre')

        file = request.files.get('audio')
        if file and file.filename:
            filename = secure_filename(file.filename)
            os.makedirs(AUDIO_DIR, exist_ok=True)
            file.save(os.path.join(AUDIO_DIR, filename))
            song.audio_file = filename

        cover = request.files.get('album_cover')
        if cover and cover.filename:
            cover_filename = secure_filename(cover.filename)
            os.makedirs(COVER_DIR, exist_ok=True)
            cover.save(os.path.join(COVER_DIR, cover_filename))
            song.album_cover = cover_filename

        release_date_str = request.form.get('release_date')
        if release_date_str:
            song.release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()

        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('edit_song.html', song=song)

@admin.route('/remove_demo/<int:song_id>', methods=['POST'])
@login_required
def removeDemo(song_id):
    admin_required()
    song = Song.query.get_or_404(song_id)
    song.audio_file = None
    db.session.commit()
    return redirect(url_for('admin.edit_song', song_id=song.id))
