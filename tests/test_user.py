import pytest
from werkzeug.test import TestResponse
from unittest.mock import patch, MagicMock
from app import db
from app import create_app
from app.models import User, Playlist, Song, linkPlaylistSong


#Test user features


#Test if passwords are saved properly to the database
def test_set_password():


   #Create a test user and set its password
   user = User(username="testUser")
   user.set_password("myPassword")


   #checking if password is stored and that password is not saved as string
   assert user.password is not None
   assert user.password != "mypassword"


#Test if the right password is stored in the database
def test_password_correct():


   #Create a test user account and set its password
   user = User(username="testUser")
   user.set_password("myPassword")


   #Check if the password in the database matchs the password attached to the user
   assert user.check_password("myPassword") == True


#Test if the database can check if the password provided is wrong or right
def test_password_incorrect():


   #Create an test user and set its password
   user = User(username="testUser")
   user.set_password("myPassword")


   #Check if the password provided is wrong
   assert user.check_password("wrongPassword") == False


#Test if database stores the password with the casing right
def test_password_case_sensitive():


   #Create a test user and set its password
   user = User(username="testUser")
   user.set_password("myPassword")


   #Check if the password matches the correct letter casing
   assert user.check_password("mypassword") == False


#Test if different users with the same password are hashed differently
def test_same_password():


   #Creates 2 test users and sets them to have the same password
   user1 = User(username="user1")
   user2 = User(username="user2")
   user1.set_password("myPassword")
   user2.set_password("myPassword")


   #Check if the passwords are hashed differently
   assert user1.password != user2.password


#Test if user has no passwords with no error
def test_empty_password():


   #Creates a test user with no passwords
   user = User(username="testUser")


   #Checks to see if the system will raise an error if the user does not have an password
   with pytest.raises(ValueError):
       user.set_password(None)


#Test if the user can have an empty string password with no error
def test_empty_string_password():
   #Create a test user
   user = User(username="testUser")


   #Checks to see if the system will raise an error if the user sets their password as an empty string
   with pytest.raises(ValueError):
       user.set_password("")


#Test user account creation
def test_signup_creates_user():
   #Create a test enviroment for flask app
   app = create_app({
       "TESTING": True,
       "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
   })


   #Do the following within the created test enviroment
   with app.app_context():
       #Create tables from models.py into the database
       db.create_all()
       #Simulate a browser
       client = app.test_client()


       #Gets the systems response from creating an user account through the route
       response = client.post('/user/creation', data={
           "username": "newuser",
           "email": "newuser@test.com",
           "password": "password123"
       })


       #Check the systems response to this request
       assert response.status_code == 302


       #Check if the user exist in the database after creation
       user = User.query.filter_by(username="newuser").first()
       assert user is not None
       assert user.email == "newuser@test.com"


       #Check if the default Favorites playlist is made for the user after account creation
       playlist = Playlist.query.filter_by(user_id=user.id).first()
       assert playlist is not None
       assert playlist.name == "Favorites"


       #Remove test information from database
       db.session.remove()
       db.drop_all()


#Test if multiple users with the same username can exist in the database
def test_signup_duplicate_username():
   #Create a test enviroment for flask app
   app = create_app({
       "TESTING": True,
       "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
   })


   #Do the following within the created test enviroment
   with app.app_context():
       #Create tables from models.py into the database
       db.create_all()
       #Simulate a browser
       client = app.test_client()


       #Create a test user account using the route
       client.post('/user/creation', data={
           "username": "duplicate",
           "email": "test1@test.com",
           "password": "password123"
       })


       #Get the systems response, when you try to create another account with the same username as test account using the route
       response = client.post('/user/creation', data={
           "username": "duplicate",
           "email": "test2@test.com",
           "password": "password123"
       })


       #Check the systems response to this request
       assert response.status_code == 302
       #Check if the database only has 1 account with the test user accounts username
       assert User.query.filter_by(username="duplicate").count() == 1


       #Remove test information from database
       db.session.remove()
       db.drop_all()


#Test if the provided email is stored in the database
def test_signup_valid_email():
   #Create a test enviroment for flask app
   app = create_app({
       "TESTING": True,
       "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
   })


   #Do the following within the created test enviroment
   with app.app_context():
       #Create tables from models.py into the database
       db.create_all()
       #Simulate a browser
       client = app.test_client()


       #Create an test user account using the route
       client.post('/user/creation', data={
           "username": "emailuser",
           "email": "valid@test.com",
           "password": "password123"
       })


       #Load the test user account infromation
       user = User.query.filter_by(username="emailuser").first()


       #Check if the user account is saved to the database and the email is attached to the user
       assert user is not None
       assert user.email == "valid@test.com"


       #Remove test information from database
       db.session.remove()
       db.drop_all()


#Test if multiple users have the same email
def test_signup_duplicate_email():
   #Create a test enviroment for flask app
   app = create_app({
       "TESTING": True,
       "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
   })


   #Do the following within the created test enviroment
   with app.app_context():
       #Create tables from models.py into the database
       db.create_all()
       #Simulate a browser
       client = app.test_client()


       #Create a test user account using the route
       client.post('/user/creation', data={
           "username": "user1",
           "email": "same@test.com",
           "password": "password123"
       })


       #Create a secondary test user account with the same email as the first test user account using the route
       client.post('/user/creation', data={
           "username": "user2",
           "email": "same@test.com",
           "password": "password123"
       })


       #Check the database if only 1 user account with the same email is saved to the database
       assert User.query.filter_by(email="same@test.com").count() == 1


       #Remove test information from database
       db.session.remove()
       db.drop_all()


#Test if the user can reset their password
def test_reset_password():
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
       user = User(username="testuser", email="test@test.com")
       user.set_password("oldPassword")
       db.session.add(user)
       db.session.commit()


       #Creates a secure token for the test user to reset their password
       from itsdangerous import URLSafeTimedSerializer
       s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
       token = s.dumps(user.email, salt='password-reset-salt')


       #The test user creates a new password using the route
       response = client.post(f'/reset_password/{token}', data={
           "password": "newPassword"
       })


       #Load the user information from the database
       updated_user = User.query.filter_by(email="test@test.com").first()


       #Check if the test users password has changed
       assert updated_user.check_password("newPassword") == True
       assert updated_user.check_password("oldPassword") == False


#Test if the forgot my password route sends an email to users
def test_forgot_password_sends_email():
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
       user = User(username="testuser", email="test@test.com")
       user.set_password("password123")
       db.session.add(user)
       db.session.commit()


       #mock smtp(Simulate sending an real email)
       with patch("smtplib.SMTP") as mock_smtp:
           #Tells system to send an email to a fake server called mock_server
           mock_server = MagicMock()
           mock_smtp.return_value.__enter__.return_value = mock_server


           #Send the email using the route
           response = client.post('/forgot', data={
               "username": "testuser"
           })


           #Check if the mock server was called
           assert mock_server.send_message.called
           #Check if the email was TLS encryptioned while being sent to mock server
           assert mock_server.starttls.called
           #Check if user was redirected to login after email was sent
           assert mock_server.login.called


#Test if the forgot my password is being called by a real user
def test_forgot_password_user_not_found():
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


       #mock smtp(Simulate sending an real email)
       with patch("smtplib.SMTP") as mock_smtp:


           #Get the system responsonse from calling the route using a user that doesn't exist
           response = client.post('/forgot', data={
               "username": "doesnotexist"
           })


           #Check if the server attemps to send an email to a user to that doesn't exist
           mock_smtp.assert_not_called()


#Test if the user can login
def test_login_success():
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


       #create a test user
       user = User(username="testuser", email="test@test.com")
       user.set_password("password123")
       db.session.add(user)
       db.session.commit()


       #Get the system response to the route being called with the test user
       response = client.post('/login', data={
           "username": "testuser",
           "password": "password123"
       }, follow_redirects=True)


       #Check the systems response to this request
       assert response.status_code == 200