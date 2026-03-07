from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes.home import homePage
    from app.routes.auth import authPage
    from app.routes.admin import admin
    app.register_blueprint(homePage)
    app.register_blueprint(authPage)
    app.register_blueprint(admin)

    with app.app_context():
        db.create_all()
    
    return app