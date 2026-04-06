from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object('config.Config')

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    from app.routes.home import homePage
    from app.routes.auth import authPage
    from app.routes.admin import admin
    from app.routes.user import user
    app.register_blueprint(homePage)
    app.register_blueprint(authPage)
    app.register_blueprint(admin)
    app.register_blueprint(user)

    with app.app_context():
        from flask_migrate import upgrade
        if not app.config.get("TESTING"):
            upgrade()

    return app