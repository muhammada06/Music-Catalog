import pytest
from datetime import date
from app.models import Playlist, Song, User, linkPlaylistSong
from unittest.mock import patch, MagicMock
from app import db, create_app
import os

# Test that song objects are created and info is saved correctly to model
def test_set_song():

    #Create test song
    song = Song(
        title="test song",
        artist="test artist",
        album="test album",
        genre="rock",
        release_date=date(2026, 1, 1),
        audio_file="testFile.mp3",
        album_cover="cover.jpg",
        online_source="https://spotify.com/test",
        user_id=1
    )

    #Check that the object is saved properly and is able to return all its attributes
    assert song.title == "test song"
    assert song.artist == "test artist"
    assert song.album == "test album"
    assert song.genre == "rock"
    assert song.release_date == date(2026, 1, 1)
    assert song.audio_file == "testFile.mp3"
    assert song.album_cover == "cover.jpg"
    assert song.online_source == "https://spotify.com/test"
    assert song.user_id == 1

#Test that songs are still created correctly when only inputting the required fields
def test_song_optional_fields():

    #Create test song with only the necessary fields of title and artist
    song = Song(
        title="test song",
        artist="test artist"
    )
    
    #Check that the object is saved properly and is able to return all its attributes
    assert song.title == "test song"
    assert song.artist == "test artist"
    assert song.album is None
    assert song.genre is None
    assert song.release_date is None
    assert song.audio_file is None
    assert song.album_cover is None
    assert song.online_source is None
    assert song.user_id is None

#Test Song objects don't interfere with each other
def test_songs_are_independent():
    #Create test song 1
    song1 = Song(title="test song", artist="artist1")

    #Create test song 2 with teh same title but different artist
    song2 = Song(title="test song", artist="artist2")

    #Check that song object 1's artist isn't the same as song object 2's
    assert song1.artist != song2.artist

# Test that song objects are created and info is saved correctly to model
def test_set_song():

    #Create test song
    song = Song(
        title="test song",
        artist="test artist",
        album="test album",
        genre="rock",
        release_date=date(2026, 1, 1),
        audio_file="testFile.mp3",
        album_cover="cover.jpg",
        online_source="https://spotify.com/test",
        user_id=1
    )

    #Check that the object is saved properly and is able to return all its attributes excluding user_id
    assert song.title == "test song"
    assert song.artist == "test artist"
    assert song.album == "test album"
    assert song.genre == "rock"
    assert song.release_date == date(2026, 1, 1)
    assert song.audio_file == "testFile.mp3"
    assert song.album_cover == "cover.jpg"
    assert song.online_source == "https://spotify.com/test"

#Test we can edit song fields
def test_update_fields():

    #Create test song
    song = Song(
        title="test song",
        artist="test artist",
        album="test album",
        genre="rock",
        release_date=date(2026, 1, 1),
        audio_file="testFile.mp3",
        album_cover="cover.jpg",
        online_source="https://spotify.com/test",
        user_id=1
    )

    #Update fields
    song.title = "new title"
    song.artist = "new artist"
    song.album = "new album"
    song.genre = "new genre"
    song.release_date = date(2025, 3, 7)
    song.audio_file = "newFile.mp3"
    song.album_cover = "newCover.jpg"
    song.online_source = "https://youtube.com/test"

    #Check if the song object attributes match the updated fields
    assert song.title == "new title"
    assert song.artist == "new artist"
    assert song.album == "new album"
    assert song.genre == "new genre"
    assert song.release_date == date(2025, 3, 7)
    assert song.audio_file == "newFile.mp3"
    assert song.album_cover == "newCover.jpg"
    assert song.online_source == "https://youtube.com/test"

#Test playing the audio stored with song
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_play_audio():
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

        #Create a test user and it to the database
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        #Create fake audio directory + file
        audio_dir = os.path.join("instance", "demo_song")
        os.makedirs(audio_dir, exist_ok=True)

        #Get the audio path in directory
        file_path = os.path.join(audio_dir, "test.mp3")
        #Write to the file as bytes
        with open(file_path, "wb") as f:
            f.write(b"fake audio content")

        #Create a song pointing to file and add it to the database
        song = Song(title="Song", artist="Artist", audio_file="test.mp3")
        db.session.add(song)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Login as second user using the route
            client.post('/login', data={
                "username": "user",
                "password": "password"
            })

            #Get the systems response from playing the audio using the route
            response = client.get(f'/user/play/{song.id}')

            #Check the systems response from this request
            assert response.status_code == 200
            assert response.data is not None

#Test preview of the song played on the site from an 3rd party
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_preview_url():
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

        #Create a test song and add/save it to the database
        song = Song(title="Song", artist="Artist", preview_url="http://fake-url")
        db.session.add(song)
        db.session.commit()

        #mock request
        with patch("requests.get") as mock_get:
            #Create a mock server for the test to be run on
            mock_response = MagicMock()
            mock_response.iter_content = lambda chunk_size: [b"audio", b"data"]
            mock_response.headers = {"Content-Type": "audio/mpeg"}
            mock_response.raise_for_status = lambda: None

            mock_get.return_value = mock_response

            #Do the following within the Simulated browser
            with client:
                #Simulate a user login using the route with the test user information
                client.post('/login', data={
                    "username": "user",
                    "password": "password"
                })

                #Get the systems response from playing the song using the route
                response = client.get(f'/user/preview/stream/{song.id}')

                #Check the systems response to this request
                assert response.status_code == 200
                #Check if the song was played
                assert response.data is not None

#Test song preview with not preview url
@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_no_preview_url():
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

        #Create a test song and add/save it to the database
        song = Song(title="Song", artist="Artist", preview_url=None)
        db.session.add(song)
        db.session.commit()

        #Do the following within the Simulated browser
        with client:
            #Simulate a user login using the route with the test user information
            client.post('/login', data={
                "username": "user",
                "password": "password"
            })

            #Get systems response from trying stream a song with no preview url
            response = client.get(f'/user/preview/stream/{song.id}')

            #Check the systems response to this request
            assert response.status_code == 404