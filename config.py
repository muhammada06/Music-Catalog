import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db' 
    UPLOAD_FOLDER = os.path.join('static', 'audio')
    SQLALCHEMY_TRACK_MODIFICATIONS = False