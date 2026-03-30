from app.models import Playlist, Song, User
from app import db

#tdd
def test_create_playlist():
    playlist = Playlist()
    assert playlist is not None

#test suite
#testing that playlist is empty when first created
def test_playlist_created_empty():
    playlist = Playlist()
    assert len(playlist.get_songs()) == 0

def test_add_song_to_playlist():
    playlist = Playlist()
    song = Song("Song1", "artist1")

    playlist.add_song(song)
    assert len(playlist.get_songs()) == 1

def test_remove_song_from_playlist():
    playlist = Playlist()
    song = Song("Song1", "Artist1")

    playlist.add_song(song)
    playlist.remove_song(song)   
    assert len(playlist.get_songs()) == 0

def test_remove_song_not_in_playlist():
    playlist = Playlist()
    song = Song("Song1", "Artist1")
    playlist.add_song(song)
    try:
      playlist.remove_song(song)
      assert True
    except:
      assert False

def test_delete_playlist(app):
    with app.app_context():
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