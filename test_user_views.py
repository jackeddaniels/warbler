"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY, do_login, session, g

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)

        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id

    def tearDown(self):
        db.session.rollback()


class MessageAddViewTestCase(UserBaseViewTestCase):

    def test_signup(self):
        """"""

        with app.test_client() as c:
            resp = c.get("/signup")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!-- Signup Template - used for testing -->", html)

    def test_signup_duplicate_inputs(self):
        """"""

        with app.test_client() as c:
            resp = c.post(
                "/signup",
                data={
                    'username':'u1',
                    'password':'123456',
                    'email':'u2@email.com',
                    'image_url':""
                })

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Username already taken", html)
            self.assertIn("Email already taken", html)
            self.assertIn("<!-- Signup Template - used for testing -->", html)


    def test_signup_null_inputs(self):
        """"""

        with app.test_client() as c:
            resp = c.post(
                "/signup",
                data={
                    'username':'',
                    'password':'123456',
                    'email':'u2@email.com',
                    'image_url':""
                })

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("This field is required.", html)
            self.assertIn("<!-- Signup Template - used for testing -->", html)


    def test_signup_logged_in(self):
        """"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

                resp = c.post(
                    "/signup",
                    data={
                        'username':'',
                        'password':'123456',
                        'email':'u2@email.com',
                        'image_url':""
                    })

                self.assertEqual(resp.status_code, 200)

                html = resp.get_data(as_text=True)
                self.assertNotIn( CURR_USER_KEY, session)
                self.assertIn("<!-- Signup Template - used for testing -->", html)


    def test_follower_logged_in(self):
        """"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/followers")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!-- Followers Template - used for testing -->", html)


    def test_follower_logged_out(self):
        """"""
        with app.test_client() as c:
            resp = c.get(f"/users/{self.u1_id}/followers",
                         follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!-- Anonymouse Home Template - used for testing  -->", html)


    def test_following_logged_in(self):
        """"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!-- Following Template - used for testing -->", html)


    def test_following_logged_out(self):
        """"""

        with app.test_client() as c:
            resp = c.get(f"/users/{self.u1_id}/following",
                         follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!-- Anonymouse Home Template - used for testing  -->", html)


    def test_add_message_logged_in(self):
        """"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/new",
                          data= {'text':'Test Message',
                                'timestamp':None,
                                'user_id': self.u1_id},
                         follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<!-- User Detail Template - used for testing -->", html)
            self.assertIn("Test Message", html)

            self.assertEqual(len(g.user.messages), 1)


    def test_add_message_logged_out(self):
        """"""

        with app.test_client() as c:
            resp = c.post(f"/messages/new",
                          data= {'text':'Test Message',
                                'timestamp':None,
                                'user_id': self.u1_id},
                         follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("<!-- Anonymouse Home Template - used for testing  -->", html)