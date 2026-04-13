from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    # Create Flask application instance
    app = Flask(__name__)

    # Load default configuration from config.py
    app.config.from_object('config.Config')

    # Override config if running in testing mode
    if test_config:
        app.config.update(test_config)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Set login route for @login_required redirects
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        # Load user from database using session-stored user ID
        from app.models import User
        return db.session.get(User, int(user_id))

    # Register application blueprints (routes)
    from app.routes.home import homePage
    from app.routes.auth import authPage
    from app.routes.admin import admin
    from app.routes.user import user
    
    app.register_blueprint(homePage)
    app.register_blueprint(authPage)
    app.register_blueprint(admin)
    app.register_blueprint(user)

    # Apply database migrations automatically (skip during testing)
    with app.app_context():
        from flask_migrate import upgrade

        if not app.config.get("TESTING"):
            upgrade()
            _seed_songs()

    return app


def _seed_songs():
    """Import songs from the bundled CSV on first launch.

    Runs only when the songs table is empty so it never overwrites
    existing data on subsequent restarts.
    """
    import csv
    import os
    from datetime import datetime
    from app.models import Song

    if Song.query.count() > 0:
        return  # Already seeded — nothing to do

    csv_path = os.path.join(os.path.dirname(__file__), 'song_catalog.csv')
    if not os.path.exists(csv_path):
        return  # CSV not present — skip silently

    imported = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            title  = (row.get('title')  or '').strip()
            artist = (row.get('artist') or '').strip()
            if not title or not artist:
                continue

            release_date = None
            for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'):
                try:
                    release_date = datetime.strptime((row.get('release_date') or '').strip(), fmt).date()
                    break
                except ValueError:
                    continue

            db.session.add(Song(
                title=title,
                artist=artist,
                album=(row.get('album') or '').strip() or None,
                genre=(row.get('genre') or '').strip() or None,
                release_date=release_date,
                album_cover=(row.get('album_cover') or '').strip() or None,
                online_source=(row.get('spotify_link') or '').strip() or None,
                audio_file=None,
                preview_url=None,
                deezer_track_id=None,
                user_id=None,
            ))
            imported += 1

    db.session.commit()
    print(f"[seed] Imported {imported} songs from song_catalog.csv")