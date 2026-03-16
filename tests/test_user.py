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