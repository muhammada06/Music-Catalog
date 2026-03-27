from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
from itsdangerous import URLSafeTimedSerializer

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
            
            return redirect(url_for('user.dashboard'))
        
        flash('Invalid email or password.', 'error')
        return render_template('login.html')
    
    return render_template('login.html')

@authPage.route('/getForgot')
def getForgot():
    return render_template('reset_password.html')

@authPage.route('/getLogin')
def getLogin():
    return render_template('login.html')

@authPage.route("/forgot", methods=["GET", "POST"])
def forgotPassword():
    if request.method == 'POST':
        username = request.form['username'].strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Username is not found! Please create an account or try again!")
            return redirect(url_for("auth.login"))
        msg = EmailMessage()
        msg['Subject'] = "Song Catalog: Forgot My Password!"
        msg['From'] = Address("Watermelion Inc.", "sajan.selvasangar", "ontariotechu.net")
        msg['To'] = user.email

        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(user.email, salt='password-reset-salt')

        link = url_for('auth.reset_password', token=token, _external=True)

        msg.set_content(f"""\
Hi {user.username}!

You have requested to reset your password! 
Click here to redirected to the reset page link:
{link}
If you did not request this link please ignore this message!

From Watermelion Inc.
""")
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login("watermelonsupport123@gmail.com", "xpkwbewagshlheig")
            smtp.send_message(msg)

    flash("Password reset link sent! Check your email.")
    return render_template("login.html")
        
@authPage.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash("The reset link is invalid or expired.")
        return render_template("login.html")

    if request.method == "POST":
        new_password = request.form['password']
        user = User.query.filter_by(email=email).first()
        user.set_password(new_password)
        db.session.commit()
        flash("Password successfully updated!")
        return render_template("login.html")

    return render_template("change_password.html")




@authPage.route("/logout")
@login_required
def logout():
    # log the user out, flash a notice and back home
    logout_user()
    flash('You have logged out.', 'logout')
    return redirect(url_for('home.home'))





    