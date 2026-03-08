from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import User
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
        new_user.set_username(request.form['username'].strip())
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
    return render_template('home.home')