from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, plain_user_password):
        self.password = generate_password_hash(plain_user_password)

    def check_password(self, plain_user_password):
        return check_password_hash(self.password, plain_user_password)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))