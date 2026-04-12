import pytest
from app import db, create_app
from app.models import User, Song

#Test Admin Features

#Test block user
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_toggle_block_user():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        # Creating admin plus a normal user
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        normal_user = User(username="user", email="user@test.com")
        normal_user.set_password("password")

        #Add created admin and user to database
        db.session.add_all([admin_user, normal_user])
        db.session.commit()

        #Logging in as admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Toggle block using a route
        response = client.post(f"/admin/toggle_block/{normal_user.id}")

        #Check if block is toggled
        assert response.status_code == 200
        data = response.get_json()

        #Check if system acknowledges the admins block
        assert data["blocked"] is True

        #Ceck if the user receives the block
        updated_user = db.session.get(User, normal_user.id)
        assert updated_user.is_blocked is True

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test to make sure admins can not delete themselves
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_cannot_delete_self():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create admin user
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        #Add a new admin account to the database
        db.session.add(admin_user)
        db.session.commit()

        #Log in as admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Attempt to delete self using a route
        response = client.post(f"/admin/delete_user/{admin_user.id}")

        #Check the systems response to admin trying to delete themselves
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "Cannot delete yourself"

        #Ensure still exists
        user = db.session.get(User, admin_user.id)
        assert user is not None

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if promote user to admin works
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_toggle_admin_role():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create admin account
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        #Create user account
        normal_user = User(username="user", email="user@test.com")
        normal_user.set_password("password")

        #Add both accounts to the database
        db.session.add_all([admin_user, normal_user])
        db.session.commit()

        #simulate a user is logged in
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Get system's response to user becoming a admin through this route
        response = client.post(f"/admin/toggle_admin/{normal_user.id}")

        #Check if the system acknowledges the user account is now an admin account
        assert response.status_code == 200
        data = response.get_json()
        assert data["is_admin"] is True

        #Check if the users account is now acknowledged as an admin account by the database
        updated_user = db.session.get(User, normal_user.id)
        assert updated_user.is_admin is True

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test to make sure admin can not block themselves
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_cannot_block_self():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create admin account
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        #Add created admin account to the database
        db.session.add(admin_user)
        db.session.commit()

        #Simulate a user is logged in as admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Get the systems response for calling the route for an admin trying to block themselves using a route
        response = client.post(f"/admin/toggle_block/{admin_user.id}")

        #Check the systems response to this request
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "Cannot block yourself"

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if an admin can delete a user using the route
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_delete_user_success():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create a test admin account
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        #Create a test user account
        normal_user = User(username="user", email="user@test.com")
        normal_user.set_password("password")

        #Add both accounts to the database
        db.session.add_all([admin_user, normal_user])
        db.session.commit()

        #Simulate the test admin logging in
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Get the systems response to the admin deleting a user using a route
        response = client.post(f"/admin/delete_user/{normal_user.id}")

        #Check the systems response to this request
        assert response.status_code == 200
        data = response.get_json()
        assert data["deleted"] is True

        #Check if the test user account exist within the database
        deleted_user = db.session.get(User, normal_user.id)
        assert deleted_user is None

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if added songs are visiable on the dashboard
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_can_view_song():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #create a test admin account
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)

        #create a test song and add it to the database
        song = Song(title="Test Song", artist="Test Artist")
        db.session.add(song)
        db.session.commit()

        #Simulate login for admin
        with client:
            client.post('/login', data={
                "username": "admin",
                "password": "adminpass"
            }, follow_redirects=True)

            #Get the dashboard visiable to admins using the route
            response = client.get('/admin/dashboard')

            #Check if the dashboard has the added song
            assert response.status_code == 200
            assert b"Test Song" in response.data

#Test if the admin can delete a song using the route
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_delete_song():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create a test admin account and add it to the database
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()  

        #create a test song and add it to the database
        song = Song(title="Delete Me", artist="Artist")
        db.session.add(song)
        db.session.commit()

        with client:
            #Simulate login for admin
            client.post('/login', data={
                "username": "admin",
                "password": "adminpass"
            }, follow_redirects=True)

            #Get the systems response to deleting the song from the database using the route
            response = client.post(f'/admin/delete/{song.id}', follow_redirects=True)

            #Check if the song still exist in the database
            assert response.status_code == 200
            assert Song.query.get(song.id) is None

#Test the admin registration route
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_registration():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Get the systems response to an admin account being created using the route
        response = client.post("/admin/creation", data={
            "username": "new_admin",
            "email": "admin@test.com",
            "password": "password"
        }, follow_redirects=True)

        #Load the created admin user information from the database
        user = User.query.filter_by(username="new_admin").first()

        #Check if the admin user infromation exist in the database and if they are considered an admin by the database
        assert user is not None
        assert user.is_admin is True

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if admin can logout
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_logout():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create a test admin account
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.set_is_admin()

        #Add it to the database
        db.session.add(admin_user)
        db.session.commit()

        #Simulate login for admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin_user.id)

        #Get systems response to logout using correct route
        response = client.get("/logout", follow_redirects=True)

        #Check the systems response to the request
        assert response.status_code == 200

        #Check if the system acknowledges the admin is logged out
        with client.session_transaction() as session:
            assert "_user_id" not in session

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test the route the admin uses to add a song
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_add_song():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create a test admin account
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()

        #Simulate login for admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin.id)

        #Get the systems response to adding a test song to the database using the route
        response = client.post('/admin/add', data={
            "title": "New Song",
            "artist": "New Artist"
        }, follow_redirects=True)

        #Check the systems response to this request
        assert response.status_code == 200

        #Check if the song exist in the database with all its information stored
        song = Song.query.filter_by(title="New Song").first()
        assert song is not None
        assert song.artist == "New Artist"

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if admin can edit songs in the catalog
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_admin_edit_song():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()
        #Simulate a browser
        client = app.test_client()

        #Create a test admin account
        admin = User(username="admin", email="admin@test.com", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)

        #Create a test song and add it to the database
        song = Song(title="Old Title", artist="Old Artist")
        db.session.add(song)
        db.session.commit()

         #Simulate login for admin
        with client.session_transaction() as session:
            session["_user_id"] = str(admin.id)

        #Get systems response to editing a song using a route
        response = client.post(f'/admin/edit/{song.id}', data={
            "title": "Updated Title",
            "artist": "Updated Artist"
        }, follow_redirects=True)

        #Check the systems response to this request
        assert response.status_code == 200

        #Check the song information in the database matches the edited information
        updated_song = db.session.get(Song, song.id)
        assert updated_song.title == "Updated Title"
        assert updated_song.artist == "Updated Artist"

        #Remove all test information from database
        db.session.remove()
        db.drop_all()

#Test if the email is stored correctly in the database
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_user_email_stored_correctly():
    """Email is stored exactly as provided."""
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()

        #Create a test user account and add it to the database
        user = User(username="test", email="test@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #Load the user information from the database
        fetched = User.query.filter_by(username="test").first()

        #Check if the user exist in the database and if the email stored in the database matches the provided email
        assert fetched is not None
        assert fetched.email == "test@example.com"

        #Remove the test information from database
        db.session.remove()
        db.drop_all()