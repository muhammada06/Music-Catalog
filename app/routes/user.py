from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Song
from app import db
from datetime import datetime

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/creation')
def creation():
    return render_template('user_account.html')