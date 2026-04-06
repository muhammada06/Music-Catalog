import pytest

from app.models import Playlist, Song, User, linkPlaylistSong
from app import db, create_app
from flask_login import login_user

#tdd
def test_create_playlist():
    playlist = Playlist(name="My Playlist", user_id=1)
    assert playlist.name == "My Playlist"
    assert playlist.user_id == 1

def test_same_playlist_name():
    # make sure different users can make the same playlist name
    p1 = Playlist(name="My Playlist", user_id=1)
    p2 = Playlist(name="My Playlist", user_id=2)
    assert p1.name == p2.name
    assert p1.user_id != p2.user_id

def test_link_playlist_song():
    playlist = Playlist(id=1, name="My Playlist", user_id=1)
    song = Song(id=1, title="Song1", artist="Artist1")
    link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)
    assert link.playlist_id == 1
    assert link.song_id == 1

def test_playlist_song_is_linked():
    playlist = Playlist(id=1, name="My Playlist", user_id=1)
    song = Song(id=1, title="Song1", artist="Artist1")
    link = linkPlaylistSong(playlist=playlist, song=song)
    assert link.playlist == playlist
    assert link.song == song

def test_delete_playlist():
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        playlist = Playlist(name="My Playlist", user_id=user.id)
        db.session.add(playlist)
        db.session.commit()

        assert Playlist.query.count() == 1

        db.session.delete(playlist)
        db.session.commit()

        assert Playlist.query.count() == 0

        db.session.remove()
        db.drop_all()

def test_playlist_name_not_empty():
    playlist = Playlist(name="Test Playlist", user_id=1)
    assert playlist.name != ""

def test_delete_playlist():
    import uuid

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        user = User(
            username=f"user_{uuid.uuid4()}",
            email=f"{uuid.uuid4()}@test.com" 
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        playlist = Playlist(name="My Playlist", user_id=user.id)
        db.session.add(playlist)
        db.session.commit()

        assert Playlist.query.count() == 1

        db.session.delete(playlist)
        db.session.commit()

        assert Playlist.query.count() == 0

        db.session.remove()
        db.drop_all()

def test_toggle_playlist_privacy():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        test_user = User(username="testuser", email="test@test.com")
        test_user.set_password("password")
        db.session.add(test_user)
        db.session.commit()

        test_playlist = Playlist(name="Test Playlist", user_id=test_user.id, is_public=False)
        db.session.add(test_playlist)
        db.session.commit()

        with app.test_request_context():
            login_user(test_user)

            test_playlist.is_public = not test_playlist.is_public
            db.session.commit()
            playlist = db.session.get(Playlist, test_playlist.id)
            assert playlist.is_public is True

            test_playlist.is_public = not test_playlist.is_public
            db.session.commit()
            playlist = db.session.get(Playlist, test_playlist.id)
            assert playlist.is_public is False       

        db.session.remove()
        db.drop_all()


@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_favorites_playlist_created():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        song = Song(title="Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        with client:
            client.post('/login', data={
                "username": "user",
                "password": "password"
            })

            client.post(f'/user/toggle_favorite/{song.id}')

            fav = Playlist.query.filter_by(name="Favorites", user_id=user.id).first()
            assert fav is not None

@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_add_to_favorites():
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
        song = Song(title="Fav Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        with client:
            client.post('/login', data={
                "username": "user",
                "password": "password"
            }, follow_redirects=True)

            #add to favorites
            response = client.post(f'/user/toggle_favorite/{song.id}')
            assert response.status_code == 200

            #check playlist exists
            fav = Playlist.query.filter_by(name="Favorites", user_id=user.id).first()
            assert fav is not None

            #check song is added
            link = linkPlaylistSong.query.filter_by(
                playlist_id=fav.id,
                song_id=song.id
            ).first()

            assert link is not None

@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_remove_from_favorites():
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
        song = Song(title="Fav Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        #add to favorites first
        fav = Playlist(name="Favorites", user_id=user.id)
        db.session.add(fav)
        db.session.flush()

        link = linkPlaylistSong(playlist_id=fav.id, song_id=song.id)
        db.session.add(link)
        db.session.commit()

        with client:
            client.post('/login', data={
                "username": "user",
                "password": "password"
            }, follow_redirects=True)

            #remove from favorites
            response = client.post(f'/user/toggle_favorite/{song.id}')
            assert response.status_code == 200

            #check removed
            link = linkPlaylistSong.query.filter_by(
                playlist_id=fav.id,
                song_id=song.id
            ).first()

            assert link is None

@pytest.mark.filterwarnings("ignore:.*Query.get.*:sqlalchemy.exc.LegacyAPIWarning")
def test_favorites_duplicates():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()

        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)

        song = Song(title="Song", artist="Artist")
        db.session.add(song)
        db.session.commit()

        with client:
            client.post('/login', data={
                "username": "user",
                "password": "password"
            })

            #add twice
            client.post(f'/user/toggle_favorite/{song.id}')
            client.post(f'/user/toggle_favorite/{song.id}')
            client.post(f'/user/toggle_favorite/{song.id}')

            fav = Playlist.query.filter_by(name="Favorites", user_id=user.id).first()

            links = linkPlaylistSong.query.filter_by(
                playlist_id=fav.id,
                song_id=song.id
            ).all()

            assert len(links) == 1

def test_playlist_created_empty():
    playlist = Playlist(name="Empty Playlist", user_id=1)
    # assuming relationship exists
    assert len(getattr(playlist, "songs", [])) == 0


def test_link_playlist_song_persisted():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        playlist = Playlist(name="Persist Playlist", user_id=user.id)
        song = Song(title="Song", artist="Artist")

        db.session.add_all([playlist, song])
        db.session.commit()

        link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)
        db.session.add(link)
        db.session.commit()

        fetched = linkPlaylistSong.query.filter_by(
            playlist_id=playlist.id,
            song_id=song.id
        ).first()

        assert fetched is not None
