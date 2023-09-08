"""Message View tests."""

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

from app import app, CURR_USER_KEY
from test_message_model import EXCESSIVE_TEXT

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


class MessageBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

        self.client = app.test_client()


class MessageAddViewTestCase(MessageBaseViewTestCase):
    def test_add_message(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of our tests
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            Message.query.filter_by(text="Hello").one()


    def test_add_message_form(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("create message page", html)

    def test_add_message_bad_data(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/messages/new", data={"text": EXCESSIVE_TEXT})
            html = resp.get_data(as_text=True)

            self.assertIn("create message page", html)
            self.assertIn("140", html)

    def test_add_message_user_not_logged_in(self):
        with self.client as c:
            resp = c.get("/messages/new")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

class MessageShowViewTestCase(MessageBaseViewTestCase):


    def test_show_message_user_not_logged_in(self):
        with self.client as c:
            resp = c.get(f"/messages/{self.m1_id}")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_show_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/messages/{self.m1_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("m1-text", html)

    def test_show_message_bad_id(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/messages/9999")

            self.assertEqual(resp.status_code, 404)

class MessageDeleteTestCase(MessageBaseViewTestCase):

    def test_delete_message_user_not_logged_in(self):
        with self.client as c:
            resp = c.post(f"/messages/{self.m1_id}/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_delete_message_bad_id(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/9999/delete")

            self.assertEqual(resp.status_code, 404)

    def test_show_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/{self.m1_id}/delete")

            self.assertEqual(resp.status_code, 302)

            empty_messages = Message.query.all()

            self.assertEqual(len(empty_messages),0)

class HomepageViewTestCase(MessageBaseViewTestCase):

    def test_show_homepage(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("m1-text", html)
            self.assertIn("home view page", html)

    def test_show_homepage_user_not_logged_in(self):
        with self.client as c:
            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("home-anon view page", html)
