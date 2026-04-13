import pytest

from app.models import Playlist, Song, User, linkPlaylistSong
from app import db, create_app
from flask_login import login_user

#Test playlist model
def test_create_playlist():
    #Create a test playlist
    playlist = Playlist(name="My Playlist", user_id=1)

    #Check if the playlist information is stored right
    assert playlist.name == "My Playlist"
    assert playlist.user_id == 1

#Test if different users can make playlists with the same name
def test_same_playlist_name():
    #Create 2 playlists with the same name but created by different users
    p1 = Playlist(name="My Playlist", user_id=1)
    p2 = Playlist(name="My Playlist", user_id=2)

    #Check if they have the same name but different creators
    assert p1.name == p2.name
    assert p1.user_id != p2.user_id

#test that users can add songs to playlists
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_add_song_to_playlist():
    #create test environment
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        #create user
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)

        #create song
        song = Song(title="Test Song", artist="Test Artist")
        db.session.add(song)
        db.session.commit()

        #create playlist
        playlist = Playlist(name="My Playlist", user_id=user.id)
        db.session.add(playlist)
        db.session.commit()

        with client:
            #login user
            client.post('/login', data={
                "username": "user",
                "password": "password"
            }, follow_redirects=True)

            #add song to playlist
            response = client.post(
                f'/user/add_to_playlist/{song.id}',
                data={"playlist_id": playlist.id},
                follow_redirects=True
            )

            #check request worked
            assert response.status_code == 200

            #check database link exists
            link = linkPlaylistSong.query.filter_by(
                playlist_id=playlist.id,
                song_id=song.id
            ).first()

            assert link is not None


#Test if the same song can be added to the playlist twice
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_add_song_duplicate():
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

        #create a test user and add the test user to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #create a test song and add it to the database
        song = Song(title="Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        #create a test playlist and add it to the database
        playlist = Playlist(name="My Playlist", user_id=user.id)
        db.session.add(playlist)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Simulate a user login using the route with the test user information
            client.post('/login', data={
                "username": "user",
                "password": "password"
            }, follow_redirects=True)

            #Add the test song to the test playlist
            client.post(f'/user/add_to_playlist/{song.id}', data={
                "playlist_id": playlist.id
            })

            #Add the test song to the test playlist again
            client.post(f'/user/add_to_playlist/{song.id}', data={
                "playlist_id": playlist.id
            })

            #Get the amount of time the test songs appear in the test playlist
            links = linkPlaylistSong.query.filter_by(
                playlist_id=playlist.id,
                song_id=song.id
            ).all()

            #Check if the test song appears in the playlist once
            assert len(links) == 1

#Test if the song is linked to the playlist in the database
def test_link_playlist_song():
    #Create a test playlist
    playlist = Playlist(id=1, name="My Playlist", user_id=1)
    #Create a test song
    song = Song(id=1, title="Song1", artist="Artist1")

    #Link the test song to the test playlist
    link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)

    #Check if the link has the test playlist and test song within the database
    assert link.playlist_id == 1
    assert link.song_id == 1

#Test if the object playlist and song are linked
def test_playlist_song_is_linked():
    #Create a test playlist
    playlist = Playlist(id=1, name="My Playlist", user_id=1)
    #Create a test song
    song = Song(id=1, title="Song1", artist="Artist1")

    #Link the test song object to the playlist object
    link = linkPlaylistSong(playlist=playlist, song=song)

    #Checks if the link is connecting the test song object to the playlist object
    assert link.playlist == playlist
    assert link.song == song

#Test if a user can delete a playlist from the database
def test_delete_playlist():
    #Create a test enviroment for flask app
    app = create_app()
    app.config['TESTING'] = True

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()

        #Create a test user and save the test user to the database
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #Create a test playlist and save the test playlist to the database
        playlist = Playlist(name="My Playlist", user_id=user.id)
        db.session.add(playlist)
        db.session.commit()

        #Check if the user only has the 1 playlist test playlist
        assert Playlist.query.count() == 1

        #Delete the playlist from the database
        db.session.delete(playlist)
        db.session.commit()

        #Check if the user has zero playlists after deleting test playlist
        assert Playlist.query.count() == 0

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if the playlist name is not empty
def test_playlist_name_not_empty():
    #Create a test playlist
    playlist = Playlist(name="Test Playlist", user_id=1)

    #Check if the playlist name is empty
    assert playlist.name != ""

#Test if the playlist can be deleted using randomly generated users
def test_delete_playlist():
    import uuid

    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()

        #Create a test user with a randomly generated user and email and add the test user to the database
        user = User(
            username=f"user_{uuid.uuid4()}",
            email=f"{uuid.uuid4()}@test.com" 
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #Create a test playlist and add the test playlist to the database
        playlist = Playlist(name="My Playlist", user_id=user.id)
        db.session.add(playlist)
        db.session.commit()

        #Check if their exist 1 playlist in the database
        assert Playlist.query.count() == 1

        #Delete the playlist from the database
        db.session.delete(playlist)
        db.session.commit()

        #Check if the playlist is deleted
        assert Playlist.query.count() == 0

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if the playlist can turned private or public using the database
def test_toggle_playlist_privacy():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()

        #Create a test user and add the test user to the database
        test_user = User(username="testuser", email="test@test.com")
        test_user.set_password("password")
        db.session.add(test_user)
        db.session.commit()

        #Create a test playlist and add the playlist to the database
        test_playlist = Playlist(name="Test Playlist", user_id=test_user.id, is_public=False)
        db.session.add(test_playlist)
        db.session.commit()

        #Do the following within the created test enviroment
        with app.test_request_context():
            #Login the test user
            login_user(test_user)

            #Turn the test playlist privacy to the opposite of its default setting and add it to the database
            test_playlist.is_public = not test_playlist.is_public
            db.session.commit()

            #Load the test playlist from the database
            playlist = db.session.get(Playlist, test_playlist.id)
            #Check if the change is stored in the database
            assert playlist.is_public is True

            #Turn the test playlist privacy to the opposite of its current setting and add it to the database
            test_playlist.is_public = not test_playlist.is_public
            db.session.commit()

            #Load the test playlist from the database
            playlist = db.session.get(Playlist, test_playlist.id)
            #Check if the change is stored in the database
            assert playlist.is_public is False       

        #Remove test information from database
        db.session.remove()
        db.drop_all()

#Test if the favourite button of the song works
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_favorites_playlist_created():
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

        #Create a test user and add the test user to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #Create a test song and add the test song to the database
        song = Song(title="Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login user using the route
            client.post('/login', data={
                "username": "user",
                "password": "password"
            })

            #Using the route allow the user to favourite a song
            client.post(f'/user/toggle_favorite/{song.id}')

            #Load the favourite playlist from the database
            fav = Playlist.query.filter_by(name="Favorites", user_id=user.id).first()

            #Check if the favourite database is empty
            assert fav is not None

#Test for adding to favourite in more detail
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_add_to_favorites():
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

        #Create a test user and add it to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)

        #Create a test song and add it to the database
        song = Song(title="Fav Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login user using the route
            client.post('/login', data={
                "username": "user",
                "password": "password"
            }, follow_redirects=True)

            #Get the system response to adding the test song to favorites
            response = client.post(f'/user/toggle_favorite/{song.id}')

            #Check the system response to this request
            assert response.status_code == 200

            #Load Favorites playlist from database
            fav = Playlist.query.filter_by(name="Favorites", user_id=user.id).first()

            #Check if Favorites playlist exists
            assert fav is not None

            #Load the link between the test song and the favourites playlist from database
            link = linkPlaylistSong.query.filter_by(
                playlist_id=fav.id,
                song_id=song.id
            ).first()

            #Check if the test song is in the favourites playlist
            assert link is not None

#Test removing song from favourite playlist
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_remove_from_favorites():
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

        #Create a test user and add it to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)

        #Create a test song and add it to the database
        song = Song(title="Fav Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        #Load test users favorites playlist
        fav = Playlist(name="Favorites", user_id=user.id)
        #Add it to the database
        db.session.add(fav)
        db.session.flush()

        #Load and link the test song to the favourites playlist
        link = linkPlaylistSong(playlist_id=fav.id, song_id=song.id)
        #Add it to the database
        db.session.add(link)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login in the test user using the route
            client.post('/login', data={
                "username": "user",
                "password": "password"
            }, follow_redirects=True)

            #Get the systems response from removing the test song from favorites using the route
            response = client.post(f'/user/toggle_favorite/{song.id}')

            #Check the systems response to this request
            assert response.status_code == 200

            #Load the link between favourites and test songs after removing test song
            link = linkPlaylistSong.query.filter_by(
                playlist_id=fav.id,
                song_id=song.id
            ).first()

            #Check if the link still exist
            assert link is None

#Test if you add to favourites twice
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_favorites_duplicates():
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

        #Create a test user and add it to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)

        #Create a test song and add it to the database
        song = Song(title="Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login the test user using the route
            client.post('/login', data={
                "username": "user",
                "password": "password"
            })

            #Favourite the test song using the route
            client.post(f'/user/toggle_favorite/{song.id}')

            #Favourite the test song using the route twice
            client.post(f'/user/toggle_favorite/{song.id}')
            client.post(f'/user/toggle_favorite/{song.id}')

            #Load the test users favourite playlist
            fav = Playlist.query.filter_by(name="Favorites", user_id=user.id).first()

            #Load the links in the favourite playlist
            links = linkPlaylistSong.query.filter_by(
                playlist_id=fav.id,
                song_id=song.id
            ).all()

            #Check if test song was only added once
            assert len(links) == 1

#Test if a playlist is empty when created
def test_playlist_created_empty():
    #Load and create the empty playlist 
    playlist = Playlist(name="Empty Playlist", user_id=1)

    # Check if a link exists
    assert len(getattr(playlist, "songs", [])) == 0

#Test if the link between playlist is saved correctly and can be retrieved from the database
def test_link_playlist_song_persisted():
    #Create a test enviroment for flask app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    #Do the following within the created test enviroment
    with app.app_context():
        #Create tables from models.py into the database
        db.create_all()

        #Create a test user and add it to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #Create a test playlist
        playlist = Playlist(name="Persist Playlist", user_id=user.id)
        #Create a test song
        song = Song(title="Song", artist="Artist")

        #Add both test playlist and song to database
        db.session.add_all([playlist, song])
        db.session.commit()

        #Link test song to test playlist and add it to the playlist
        link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)
        db.session.add(link)
        db.session.commit()

        #Load the playlist link from the database
        fetched = linkPlaylistSong.query.filter_by(
            playlist_id=playlist.id,
            song_id=song.id
        ).first()

        #Check if the playlist is in the database and can be retrieved
        assert fetched is not None
        assert fetched.playlist_id == playlist.id
        assert fetched.song_id == song.id

#Test if the private playlist is hidden from other users
def test_private_playlist_is_hidden():
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

        #Create the first test user and it to the database
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        db.session.add(user1)
        db.session.commit()

        #Create a test private playlist for first user and it to the database
        private_playlist = Playlist(
            name="Private Playlist",
            user_id=user1.id,
            is_public=False
        )
        db.session.add(private_playlist)
        db.session.commit()

        #Create the second test user and add it to the database
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login as second user using the route
            client.post('/login', data={
                "username": "user2",
                "password": "password"
            }, follow_redirects=True)

            #Get the systems response from trying to view the first user's private playlist using the route
            response = client.get(f'/user/playlist/view/{private_playlist.id}')

            #Check the systems response to this request
            assert response.status_code == 404

#Test if the public playlist is visiable to other users
def test_public_playlist_visible():
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

        #Create the first test user and it to the database
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        db.session.add(user1)
        db.session.commit()

        #Create a test public playlist for first user and add it to the database
        public_playlist = Playlist(
            name="Public Playlist",
            user_id=user1.id,
            is_public=True
        )
        db.session.add(public_playlist)
        db.session.commit()

        #Create the second test user and add it to the database
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login as second user using the route
            client.post('/login', data={
                "username": "user2",
                "password": "password"
            }, follow_redirects=True)

            #Get the systems response from trying to view the first user's public playlist using the route
            response = client.get(f'/user/playlist/view/{public_playlist.id}')

            #Check the systems response to this request
            assert response.status_code == 200