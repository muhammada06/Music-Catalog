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

    return app