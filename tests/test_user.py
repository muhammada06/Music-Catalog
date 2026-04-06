import pytest
from werkzeug.test import TestResponse
from app import db
from app import create_app
from app.models import User, Playlist

def test_set_password():
    user = User(username="testUser")
    user.set_password("myPassword")

    #checking if password is stored and that password is not saved as string
    assert user.password is not None
    assert user.password != "mypassword"

def test_password_correct():
    user = User(username="testUser")
    user.set_password("myPassword")
    assert user.check_password("myPassword") == True

def test_password_incorrect():
    user = User(username="testUser")
    user.set_password("myPassword")
    assert user.check_password("wrongPassword") == False

def test_password_case_sensitive():
    user = User(username="testUser")
    user.set_password("myPassword")
    assert user.check_password("mypassword") == False

def test_same_password():
    #checks that passwords are hashed differently
    user1 = User(username="user1")
    user2 = User(username="user2")
    user1.set_password("myPassword")
    user2.set_password("myPassword")
    assert user1.password != user2.password

def test_empty_password():
    user = User(username="testUser")

    with pytest.raises(ValueError):
        user.set_password(None)

def test_empty_string_password():
    user = User(username="testUser")

    with pytest.raises(ValueError):
        user.set_password("")

def test_signup_creates_user():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        client = app.test_client()

        response = client.post('/user/creation', data={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert response.status_code == 302

        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.email == "newuser@test.com"

        playlist = Playlist.query.filter_by(user_id=user.id).first()
        assert playlist is not None
        assert playlist.name == "Favorites"

        db.session.remove()
        db.drop_all()

def test_signup_duplicate_username():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        client.post('/user/creation', data={
            "username": "duplicate",
            "email": "test1@test.com",
            "password": "password123"
        })

        response = client.post('/user/creation', data={
            "username": "duplicate",
            "email": "test2@test.com",
            "password": "password123"
        })

        # still redirects (expected)
        assert response.status_code == 302

        # BUT only one user should exist
        assert User.query.filter_by(username="duplicate").count() == 1

        db.session.remove()
        db.drop_all()

def test_reset_password():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        #create testing user
        user = User(username="testuser", email="test@test.com")
        user.set_password("oldPassword")
        db.session.add(user)
        db.session.commit()

        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = s.dumps(user.email, salt='password-reset-salt')

        #create new password
        response = client.post(f'/reset_password/{token}', data={
            "password": "newPassword"
        })

        updated_user = User.query.filter_by(email="test@test.com").first()

        assert updated_user.check_password("newPassword") == True
        assert updated_user.check_password("oldPassword") == False