import pytest
from app.models import Playlist, Song, linkPlaylistSong

def test_create_playlist():
    playlist = Playlist(name="My Playlist", user_id=1)
    assert playlist.name == "My Playlist"
    assert playlist.user_id == 1

def test_same_playlist_name_different_users():
    p1 = Playlist(name="My Playlist", user_id=1)
    p2 = Playlist(name="My Playlist", user_id=2)

    assert p1.name == p2.name
    assert p1.user_id != p2.user_id

def test_link_song_to_playlist():
    playlist = Playlist(id=1, name="My Playlist", user_id=1)
    song = Song(id=1, title="Song1", artist="Artist1")

    link = linkPlaylistSong(playlist_id=playlist.id, song_id=song.id)

    assert link.playlist_id == 1
    assert link.song_id == 1


def test_playlist_song_relationship_objects():
    playlist = Playlist(id=1, name="My Playlist", user_id=1)
    song = Song(id=1, title="Song1", artist="Artist1")

    link = linkPlaylistSong(playlist=playlist, song=song)

    assert link.playlist == playlist
    assert link.song == song
    
def test_song_objects_are_distinct():
    song1 = Song(title="Song1", artist="Artist1")
    song2 = Song(title="Song1", artist="Artist1")

    assert song1 != song2


def test_playlist_name_not_none():
    playlist = Playlist(name="Test Playlist", user_id=1)

    assert playlist.name is not None

