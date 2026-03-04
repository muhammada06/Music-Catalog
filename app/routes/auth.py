from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

authPage = Blueprint('auth', __name__)

@authPage.route("/register", methods=["GET", "POST"])
def create_account():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

    




    