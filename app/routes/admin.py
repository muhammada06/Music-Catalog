from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Song
from app import db
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin.route('/dashboard')
@login_required
def dashboard():
    admin_required()
    songs = Song.query.filter_by(user_id=current_user.id).all()
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

        song = Song(
            title=request.form.get('title'),
            artist=request.form.get('artist'),
            album=request.form.get('album'),
            genre=request.form.get('genre'),
            release_date=release_date,
            user_id=current_user.id

        )

        db.session.add(song)
        db.session.commit()

        return redirect(url_for('admin.dashboard'))

    return render_template('add_song.html')

@admin.route('/delete')
@login_required
def delete_page():
    admin_required()
    songs = Song.query.filter_by(user_id=current_user.id).all()
    return render_template('delete_song.html', songs=songs)

@admin.route('/delete/<int:song_id>', methods=['POST'])
@login_required
def delete_song(song_id):
    admin_required()

    song = Song.query.get_or_404(song_id)

    # Only allow deleting your own songs
    if song.user_id != current_user.id:
        abort(403)

    db.session.delete(song)
    db.session.commit()

    return redirect(url_for('admin.delete_page'))