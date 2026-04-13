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


# ── Login / Logout ────────────────────────────────────────────────────────────

@authPage.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login (GET/POST).

    GET  – renders the login form.
    POST – validates credentials; blocks access for blocked accounts;
           redirects admins to the admin panel, regular users to their playlists.
    """
    # Redirect already-authenticated users away from the login page
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Prevent blocked accounts from signing in
            if user.is_blocked:
                flash('Your account has been blocked. Contact an administrator.', 'error')
                return render_template('login.html')
            login_user(user)
            # Route admins to the admin panel, regular users to their dashboard
            if user.is_admin:
                return redirect(url_for('admin.home'))
            return redirect(url_for('user.browse_playlists'))

        flash('Invalid email or password.', 'error')
        return render_template('login.html')

    return render_template('login.html')


@authPage.route('/getForgot')
def getForgot():
    """Render the forgot-password request page."""
    return render_template('reset_password.html')


@authPage.route('/getLogin')
def getLogin():
    """Render the login page (GET-only helper route)."""
    return render_template('login.html')


# ── Password Reset ────────────────────────────────────────────────────────────

@authPage.route("/forgot", methods=["GET", "POST"])
def forgotPassword():
    """Send a password-reset email to the user (POST).

    Looks up the submitted username, generates a time-limited signed token
    via itsdangerous, and emails a reset link to the user's registered address.
    The token expires after 1 hour (enforced in reset_password).
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Username is not found! Please create an account or try again!")
            return redirect(url_for("auth.login"))

        # Build the plain-text reset email
        msg = EmailMessage()
        msg['Subject'] = "Song Catalog: Forgot My Password!"
        msg['From'] = Address("Watermelion Inc.", "sajan.selvasangar", "ontariotechu.net")
        msg['To'] = user.email

        # Sign the user's email address into a URL-safe token with a fixed salt
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
        # Send via Gmail SMTP using TLS
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login("watermelonsupport123@gmail.com", "xpkwbewagshlheig")
            smtp.send_message(msg)

    flash("Password reset link sent! Check your email.")
    return render_template("login.html")


@authPage.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Validate the reset token and allow the user to set a new password.

    GET  – verifies the token (max age 1 hour) and renders the change-password form.
    POST – updates the user's hashed password in the database.

    If the token is invalid or expired, the user is redirected to login with an error.
    """
    try:
        # Decode and verify the signed token; raises if expired or tampered
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


# ── Logout ────────────────────────────────────────────────────────────────────

@authPage.route("/logout")
@login_required
def logout():
    """Log the current user out and redirect to the homepage."""
    logout_user()
    flash('You have logged out.', 'logout')
    return redirect(url_for('home.home'))

# ── User Manual ────────────────────────────────────────────────────────────────────

@authPage.route("/pdf")
def open_pdf():
    """Open user manual"""
    return redirect(url_for('static', filename='user_manual.pdf'))
