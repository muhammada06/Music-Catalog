from app.models import Playlist, Song, User, linkPlaylistSong
from app import db, create_app

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