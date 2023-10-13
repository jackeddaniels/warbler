"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id


    def tearDown(self):
        db.session.rollback()


    def test_message_model(self):
        """Test new message attributes"""
        u1 = User.query.get(self.u1_id)
        msg = Message(text='Test text', timestamp=None, user_id=u1.id)

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(u1.messages[0], msg)
        self.assertEqual(len(u1.messages[0].liking_users), 0)

    # TODO: Ask if more is needed


