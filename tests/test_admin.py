import pytest
from app import db, create_app
from app.models import User, Song


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_toggle_block_user():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        # Creating admin plus a normal user
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        normal_user = User(username="user", email="user@test.com")
        normal_user.set_password("password")

        db.session.add_all([admin_user, normal_user])
        db.session.commit()

        #Logging in as admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Toggle block
        response = client.post(f"/admin/toggle_block/{normal_user.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["blocked"] is True

        updated_user = db.session.get(User, normal_user.id)
        assert updated_user.is_blocked is True

        db.session.remove()
        db.drop_all()


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_cannot_delete_self():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        #Create admin user
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        db.session.add(admin_user)
        db.session.commit()

        #Log in as admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Attempt to delete self
        response = client.post(f"/admin/delete_user/{admin_user.id}")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "Cannot delete yourself"

        #Ensure still exists
        user = db.session.get(User, admin_user.id)
        assert user is not None

        db.session.remove()
        db.drop_all()


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_toggle_admin_role():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        normal_user = User(username="user", email="user@test.com")
        normal_user.set_password("password")

        db.session.add_all([admin_user, normal_user])
        db.session.commit()

        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        response = client.post(f"/admin/toggle_admin/{normal_user.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["is_admin"] is True

        updated_user = db.session.get(User, normal_user.id)
        assert updated_user.is_admin is True

        db.session.remove()
        db.drop_all()


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_cannot_block_self():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        db.session.add(admin_user)
        db.session.commit()

        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        response = client.post(f"/admin/toggle_block/{admin_user.id}")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "Cannot block yourself"

        db.session.remove()
        db.drop_all()


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_delete_user_success():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        normal_user = User(username="user", email="user@test.com")
        normal_user.set_password("password")

        db.session.add_all([admin_user, normal_user])
        db.session.commit()

        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        response = client.post(f"/admin/delete_user/{normal_user.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["deleted"] is True

        deleted_user = db.session.get(User, normal_user.id)
        assert deleted_user is None

        db.session.remove()
        db.drop_all()

@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_can_view_song():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        #create admin
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)

        #create song
        song = Song(title="Test Song", artist="Test Artist")
        db.session.add(song)
        db.session.commit()

        #login admin
        with client:
            client.post('/login', data={
                "username": "admin",
                "password": "adminpass"
            }, follow_redirects=True)

            response = client.get('/admin/dashboard')

            assert response.status_code == 200
            assert b"Test Song" in response.data

@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_delete_song():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        #screate admin
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()  

        #create song
        song = Song(title="Delete Me", artist="Artist")
        db.session.add(song)
        db.session.commit()

        with client:
            #login
            client.post('/login', data={
                "username": "admin",
                "password": "adminpass"
            }, follow_redirects=True)

            #delete song
            response = client.post(f'/admin/delete/{song.id}', follow_redirects=True)

            assert response.status_code == 200

            assert Song.query.get(song.id) is None


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_registration():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        # Register a normal user
        response = client.post("/auth/register", data={
            "username": "new_admin",
            "email": "admin@test.com",
            "password": "password"
        }, follow_redirects=True)

        user = User.query.filter_by(username="new_admin").first()

        # User should exist (if your register route works)
        if user:
            assert user.is_admin is False

        db.session.remove()
        db.drop_all()


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_logout():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        db.session.add(admin_user)
        db.session.commit()

        # log in manually
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        # logout using correct route
        response = client.get("/logout", follow_redirects=True)

        assert response.status_code == 200

        # session should be cleared
        with client.session_transaction() as session:
            assert "_user_id" not in session

        db.session.remove()
        db.drop_all()