from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

authPage = Blueprint('auth', __name__)
     



@authPage.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password=request.form['password']
        user= User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            
            return redirect(url_for('home.home'))
        
        flash('Invalid email or password.', 'error')
        return render_template('login.html')
    
    return render_template('login.html')    


@authPage.route("/logout")
@login_required
def logout():
    # log the user out, flash a notice and back home
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('home.home'))





    