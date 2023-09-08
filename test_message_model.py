"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Like, DEFAULT_IMAGE_URL
from sqlalchemy.exc import IntegrityError, DataError

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

EXCESSIVE_TEXT = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum."""

class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        message = Message(text="test",user_id=self.u1_id)

        db.session.add(message)
        db.session.commit()

        self.msg_id = message.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_message_model(self):
        message = Message.query.get(self.msg_id)

        self.assertEqual(message.text, "test")
        self.assertEqual(message.user_id, self.u1_id)

    def test_message_instantiation_no_text(self):
        message_no_text = Message(
                    text=None,
                    user_id=self.u1_id
        )

        db.session.add(message_no_text)
        with self.assertRaises(IntegrityError):
            db.session.commit()


    def test_message_instantiation_bad_user_id(self):
        message_bad_user_id = Message(
                    text="text",
                    user_id=5000000
        )

        db.session.add(message_bad_user_id)
        with self.assertRaises(IntegrityError):
            db.session.commit()


    def test_message_instantiation_text_too_long(self):
        message_excessive_text = Message(
                    text=EXCESSIVE_TEXT,
                    user_id=self.u1_id
        )

        db.session.add(message_excessive_text)
        with self.assertRaises(DataError):
            db.session.commit()

    def test_user_linked_to_message(self):
        message = Message.query.get(self.msg_id)

        self.assertEqual(message.user_id, self.u1_id)


    def test_message_user_relationship(self):
        message = Message.query.get(self.msg_id)
        user = User.query.get(self.u1_id)

        self.assertEqual(message.user.id, user.id)
        self.assertIn(message, user.messages)


    def test_like_relationship(self):
        message = Message.query.get(self.msg_id)
        user = User.query.get(self.u1_id)
        like = Like(user_id = user.id, message_id = message.id)

        db.session.add(like)
        db.session.commit()

        self.assertEqual((like.user_id,like.message_id), (user.id, message.id))

        self.assertIn(message, user.liked_messages)
        self.assertIn(user, message.users_liked)
