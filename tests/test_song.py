from app.models import Song
from datetime import date

# checking that songs are created and info is saved correctly
def test_set_song():
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

    assert song.title == "test song"
    assert song.artist == "test artist"
    assert song.album == "test album"
    assert song.genre == "rock"
    assert song.release_date == date(2026, 1, 1)
    assert song.audio_file == "testFile.mp3"
    assert song.album_cover == "cover.jpg"
    assert song.online_source == "https://spotify.com/test"
    assert song.user_id == 1

#checking that songs are still created correctly when only inputting the required fields
def test_song_optional_fields():
    song = Song(
        title="test song",
        artist="test artist"
    )

    assert song.title == "test song"
    assert song.artist == "test artist"
    assert song.album is None
    assert song.genre is None
    assert song.release_date is None
    assert song.audio_file is None
    assert song.album_cover is None
    assert song.online_source is None
    assert song.user_id is None

def test_songs_are_independent():
    song1 = Song(title="test song", artist="artist1")
    song2 = Song(title="test song", artist="artist2")
    assert song1.artist != song2.artist

#checking we can edit fields
def test_update_fields():
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

    # update fields
    song.title = "new title"
    song.artist = "new artist"
    song.album = "new album"
    song.genre = "new genre"
    song.release_date = date(2025, 3, 7)
    song.audio_file = "newFile.mp3"
    song.album_cover = "newCover.jpg"
    song.online_source = "https://youtube.com/test"

    assert song.title == "new title"
    assert song.artist == "new artist"
    assert song.album == "new album"
    assert song.genre == "new genre"
    assert song.release_date == date(2025, 3, 7)
    assert song.audio_file == "newFile.mp3"
    assert song.album_cover == "newCover.jpg"
    assert song.online_source == "https://youtube.com/test"