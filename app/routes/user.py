import os

from flask import Blueprint, current_app, render_template, request, redirect, send_file, send_from_directory, url_for, abort, flash
from flask_login import login_required, current_user
from app.models import User, Song
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
    return render_template("user_dashboard.html", songs=songs)


@user.route('/play/<int:song_id>')
@login_required
def play(song_id):
    song = Song.query.get_or_404(song_id)
    folder_path = os.path.abspath(os.path.join('instance', 'demo_song'))

    return send_from_directory(folder_path, song.audio_file)