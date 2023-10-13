"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follow, DEFAULT_IMAGE_URL, DEFAULT_HEADER_IMAGE_URL

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Test new user attributes"""
        u1 = User.query.get(self.u1_id)

        self.assertEqual(u1.email, "u1@email.com")
        self.assertEqual(u1.image_url, DEFAULT_IMAGE_URL)
        self.assertEqual(u1.header_image_url, DEFAULT_HEADER_IMAGE_URL)
        self.assertEqual(u1.bio, "")
        self.assertEqual(u1.location, "")
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)


    def test_is_following_valid(self):
        """Test if is_following can detect if u1 follows u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True)


    def test_is_following_invalid(self):
        """Test if is_following can detect if u1 isn't following u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        self.assertEqual(user1.is_following(user2), False)


    def test_is_followed_by_valid(self):
        """Test if is_followed_by can detect if u1 is followed by u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        user1.followers.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), True)


    def test_is_followed_by_invalid(self):
        """Test if is_followed_by can detect if u1 is not followed by u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        self.assertEqual(user1.is_followed_by(user2), False)


    def test_signup_valid(self):
        """Test if signup successfully creates a new user with valid credentials"""

        test_user = User.signup(
            username='Test',
            email='test@gmail.com',
            password='password',
            image_url=None)

        db.session.commit()

        test_u_id = test_user.id

        test_user_profile = User.query.get(test_u_id)

        self.assertEqual(test_user_profile.username, 'Test')
        self.assertEqual(test_user_profile.email, 'test@gmail.com')
        self.assertEqual(test_user_profile.image_url, DEFAULT_IMAGE_URL)
        self.assertNotEqual(test_user_profile.password, 'password')


    def test_signup_invalid_unique(self):
        """Test if signup rejects duplicate usernames"""

        with self.assertRaises(IntegrityError):

            User.signup(
                username='u1',
                email='test@gmail.com',
                password='password',
                image_url=None)

            db.session.commit()


    def test_signup_invalid_null(self):
        """Test if signup rejects null input for non-nullable fields"""

        with self.assertRaises(ValueError):

            User.signup(
                username='Test',
                email='test@gmail.com',
                password='',
                image_url=None)

            db.session.commit()


    def test_authenticate_valid(self):
        """Test if authenticate is successful on valid username and password"""

        user = User.query.get(self.u1_id)

        auth = User.authenticate(user.username, 'password')

        self.assertEqual(auth, user)


    def test_authenticate_invalid_username(self):
            """Test if authenticate fails when invalid username"""

            auth = User.authenticate('12345', 'password')

            self.assertEqual(auth, False)


    def test_authenticate_invalid_password(self):
            """Test if authenticate fails when invalid password"""

            auth = User.authenticate('u1', 'fake')

            self.assertEqual(auth, False)