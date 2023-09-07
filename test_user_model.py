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

TEST_IMAGE_URL = 'https://upload.wikimedia.org/wikipedia/commons/'\
                            'thumb/1/11/Canis_lupus_familiaris.002_-_Monfero.j'\
                            'pg/640px-Canis_lupus_familiaris.002_-_Monfero.jpg'


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_is_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        follow = Follow(
            user_being_followed_id=self.u2_id,
            user_following_id=self.u1_id
        )

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))

    def test_is_not_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_following(u2))

    def test_is_followed_by(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        follow = Follow(
            user_being_followed_id=self.u2_id,
            user_following_id=self.u1_id
        )

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))

    def test_is_not_followed_by(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u2.is_followed_by(u1))

    def test_user_sign_up(self):
        new_user3 = User.signup("u3", "u3@email.com", "password", None)
        new_user4 = User.signup(
                            "u4",
                            "u4@email.com",
                            "password",
                            TEST_IMAGE_URL)

        db.session.commit()

        u3_id = new_user3.id
        u4_id = new_user4.id

        u3 = User.query.get(u3_id)
        u4 = User.query.get(u4_id)

        self.assertEqual((u3.username), 'u3')
        self.assertEqual((u3.email), 'u3@email.com')
        self.assertIn('$2b$', (u3.password))
        self.assertEqual((u3.image_url), DEFAULT_IMAGE_URL)
        self.assertEqual((u4.image_url), TEST_IMAGE_URL)

    def test_user_sign_up_fails(self):

        self.assertRaises(
                    IntegrityError,
                    User.signup,
                    "u2",
                    "u2@email.com",
                    "password",
                    None
        )
        self.assertRaises(
                    IntegrityError,
                    User.signup,
                    "u4",
                    "u4@email.com",
                    TEST_IMAGE_URL,
                    password = None
        )


