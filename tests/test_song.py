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
        user_id=1
    )

    assert song.title == "test song"
    assert song.artist == "test artist"
    assert song.album == "test album"
    assert song.genre == "rock"
    assert song.release_date == date(2026, 1, 1)
    assert song.audio_file == "testFile.mp3"
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
    assert song.audio_file is None
    assert song.release_date is None

def test_songs_are_independent():
    song1 = Song(title="test song", artist="artist1")
    song2 = Song(title="test song", artist="artist2")
    assert song1.artist != song2.artist