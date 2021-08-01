import unittest
from time import sleep

from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        
    def test_wrong_password_verification(self):
        u = User(password='cat')
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_token_confirmation(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_change_email_token_confirmation(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('newemail@mail.com')
        self.assertTrue(u.confirm_email_change(token))

    def test_token_expiration(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        sleep(2)
        self.assertFalse(u.confirm(token))

    def test_change_email_token_expiration(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token(
            'newemail@mail.com',
            expiration=1,
        )
        sleep(2)
        self.assertFalse(u.confirm_email_change(token))

    def test_token_unique(self):
        u = User(password='cat')
        u2 = User(password='cat')
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_change_email_token_unique(self):
        u = User(password='cat')
        u2 = User(password='cat')
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        token = u.generate_email_change_token('newemail@mail.com')
        self.assertFalse(u2.confirm_email_change(token))

    def test_change_email_duplicate(self):
        u = User(password='cat')
        u2 = User(password='cat')
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        token = u.generate_email_change_token('newemail@mail.com')
        u.confirm_email_change(token)
        token2 = u2.generate_email_change_token('newemail@mail.com')
        self.assertFalse(u2.confirm_email_change(token2))

    def test_check_user(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u == User.check_user(token))

    def test_check_user_expired(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        sleep(2)
        self.assertFalse(u == User.check_user(token))

    def test_get_avatar_link_default(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        link = u.get_avatar_link()
        self.assertTrue(link == '/static/profile_image/default-avatar.jpg')

    def test_get_avatar_link(self):
        u = User(password='cat')
        u.avatar_link = 'link.jpg'
        db.session.add(u)
        db.session.commit()
        link = u.get_avatar_link()
        self.assertTrue(link == '/static/profile_image/link.jpg')
