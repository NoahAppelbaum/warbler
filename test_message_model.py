"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follow, DEFAULT_IMAGE_URL
from sqlalchemy.exc import IntegrityError

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

    # def test_message_instantiation_exceptions(self):

        #TODO: implement `with self.assertRaises(Exception): ...`

        # message_no_text = Message(
        #             text=None,
        #             user_id=self.u1_id
        # )

        # message_bad_user_id = Message(
        #             text="text",
        #             user_id=50000
        # )

        # db.session.add(message_no_text)
        # self.assertRaises(ValueError, db.session.commit())

        # db.session.add(message_bad_user_id)
        # self.assertRaises(IntegrityError, db.session.commit())

    def test_user_linked_to_message(self):
        message = Message.query.get(self.msg_id)

        self.assertEqual(message.user.id, self.u1_id)
        self.assertEqual(message.user_id, self.u1_id)
