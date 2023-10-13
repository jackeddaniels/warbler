"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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


# Does is_following successfully detect when user1 is following user2?
    def test_is_following_valid(self):
        """Test if is_following can detect if u1 follows u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True)

# Does is_following successfully detect when user1 is not following user2?
    def test_is_following_invalid(self):
        """Test if is_following can detect if u1 isn't following u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        self.assertEqual(user1.is_following(user2), False)


# Does is_followed_by successfully detect when user1 is followed by user2?
    def test_is_followed_by(self):
        """Test if is_followed can detect if u1 is followed by u2"""

        user1 = User.query.get(self.u1_id)
        user2 = User.query.get(self.u2_id)

        user1.followers.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), True)

# Does is_followed_by successfully detect when user1 is not followed by user2?
# Does User.signup successfully create a new user given valid credentials?
# Does User.signup fail to create a new user if any of the validations (eg uniqueness, non-nullable fields) fail?
# Does User.authenticate successfully return a user when given a valid username and password?
# Does User.authenticate fail to return a user when the username is invalid?
# Does User.authenticate fail to return a user when the password is invalid?