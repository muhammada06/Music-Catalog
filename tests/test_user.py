import pytest

from app.models import User

def test_set_password():
    user = User(username="testUser")
    user.set_password("myPassword")

    #checking if password is stored and that password is not saved as string
    assert user.password is not None
    assert user.password != "mypassword"

def test_password_correct():
    user = User(username="testUser")
    user.set_password("myPassword")
    assert user.check_password("myPassword") == True

def test_password_incorrect():
    user = User(username="testUser")
    user.set_password("myPassword")
    assert user.check_password("wrongPassword") == False

def test_password_case_sensitive():
    user = User(username="testUser")
    user.set_password("myPassword")
    assert user.check_password("mypassword") == False

def test_same_password():
    #checks that passwords are hashed differently
    user1 = User(username="user1")
    user2 = User(username="user2")
    user1.set_password("myPassword")
    user2.set_password("myPassword")
    assert user1.password != user2.password

def test_empty_password():
    user = User(username="testUser")

    with pytest.raises(ValueError):
        user.set_password(None)