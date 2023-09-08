"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, session, CURR_USER_KEY
from flask import g

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
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id

        self.client = app.test_client()

class UserSignupViewTestCase(UserBaseViewTestCase):

    def test_show_signup_form(self):
        with self.client as c:

            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("user signup page", html)

    def test_user_signup(self):
        with self.client as c:

            resp = c.post("/signup", data={
                                            "username": "test",
                                            "password": "password",
                                            "email": "test@email.com",
                                            "image_url": ""
            })

            self.assertEqual(resp.status_code, 302)
            User.query.filter_by(username="test").one()

class UserLogInViewTestCase(UserBaseViewTestCase):


    def test_user_login(self):
        with self.client as c:

            resp = c.post("/login", data={
                                            "username": "u1",
                                            "password": "password",
            })

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location,"/")
            self.assertEqual(session[CURR_USER_KEY],self.u1_id)


    def test_user_login_failed(self):
        with self.client as c:

            resp = c.post("/login", data={
                                            "username": "u1",
                                            "password": "123456",
            })

            html = resp.get_data(as_text=True)
            self.assertIn("Invalid credentials.", html)


class UserLogOutViewTestCase(UserBaseViewTestCase):

    def test_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("logout")

            self.assertEqual(resp.location,"/login")
            self.assertNotIn(CURR_USER_KEY,session)