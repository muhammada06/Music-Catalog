from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, send_from_directory, jsonify
from flask_login import login_required, current_user
from app.models import Song, User
from app import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import csv
import io
import json
import requests

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

        existing_email = User.query.filter_by(email=request.form['email'].strip()).first()
        if existing_email:
            flash("Email already registered. Try logging in or use a different email.")
            return redirect(url_for("auth.login"))
        
        new_user.set_email(request.form['email'].strip())
        new_user.set_is_admin()
        db.session.add(new_user)
        db.session.commit()
        flash("Admin account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))

@admin.route('/home')
@login_required
def home():
    admin_required()
    return render_template('admin_home.html')

@admin.route('/accounts')
@login_required
def accounts():
    admin_required()
    users = User.query.order_by(User.is_admin.desc(), User.username).all()
    return render_template('admin_accounts.html', users=users)

@admin.route('/toggle_block/<int:user_id>', methods=['POST'])
@login_required
def toggle_block(user_id):
    admin_required()
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot block yourself'}), 400
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    return jsonify({'blocked': user.is_blocked})

@admin.route('/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    admin_required()
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot change your own role'}), 400
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'is_admin': user.is_admin})

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    admin_required()
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'deleted': True})

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

        title = request.form.get('title')
        artist = request.form.get('artist')
      
        song = Song(
            title=title,
            artist=artist,
            album=request.form.get('album'),
            genre=request.form.get('genre'),
            release_date=release_date,
            audio_file=audio_filename,
            album_cover=cover_filename,
            online_source=request.form.get('online_source'),
            preview_url=None,        
            deezer_track_id=None,  
            user_id=current_user.id
        )

        db.session.add(song)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('add_song.html')


COLUMN_MAP = {
    'title':        'title',
    'artist':       'artist',
    'album':        'album',
    'genre':        'genre',
    'release_date': 'release_date',
    'album_cover':  'album_cover',
    'spotify_link': 'online_source',
}

def map_columns(row: dict) -> dict:
    result = {}
    for key, value in row.items():
        normalized = key.strip().lower()
        if normalized in COLUMN_MAP:
            result[COLUMN_MAP[normalized]] = value
    return result

@admin.route('/import', methods=['POST'])
@login_required
def import_songs():
    admin_required()
    file = request.files.get('import_file')
    if not file or not file.filename:
        flash("No file uploaded.")
        return redirect(url_for('admin.dashboard'))

    raw = file.read().decode('utf-8', errors='replace')
    fname = file.filename.lower()

    if fname.endswith('.csv'):
        rows = list(csv.DictReader(io.StringIO(raw)))
    elif fname.endswith('.json'):
        try:
            rows = json.loads(raw)
            if not isinstance(rows, list):
                flash("JSON must be an array of objects.")
                return redirect(url_for('admin.dashboard'))
        except json.JSONDecodeError:
            flash("Invalid JSON file.")
            return redirect(url_for('admin.dashboard'))
    else:
        flash("Unsupported file type. Upload .csv or .json.")
        return redirect(url_for('admin.dashboard'))

    imported = skipped = 0
    for row in rows:
        mapped = map_columns(row)
        title  = (mapped.get('title')  or '').strip()
        artist = (mapped.get('artist') or '').strip()
        if not title or not artist:
            skipped += 1
            continue

        release_date = None
        for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'):
            try:
                release_date = datetime.strptime((mapped.get('release_date') or '').strip(), fmt).date()
                break
            except ValueError:
                continue

        print(f"Fetching preview for: {title}")

        song = Song(
            title=title,
            artist=artist,
            album=(mapped.get('album') or '').strip() or None,
            genre=(mapped.get('genre') or '').strip() or None,
            release_date=release_date,
            audio_file=None,
            album_cover=((mapped.get('album_cover') or '')[:255]) or None,
            online_source=(mapped.get('online_source') or '').strip() or None,
            preview_url=None,       
            deezer_track_id=None, 
            user_id=current_user.id
        )
        db.session.add(song)
        imported += 1

    try:
        db.session.commit()
        flash(f"Successfully imported {imported} song(s).")
        if skipped:
            flash(f"Skipped {skipped} row(s) — missing title or artist.")
    except Exception:
        db.session.rollback()
        flash("Database error during import.")

    return redirect(url_for('admin.dashboard'))


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

        song.online_source = ','.join(u.strip() for u in request.form.getlist('online_sources') if u.strip())

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
