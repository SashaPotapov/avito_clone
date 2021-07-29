import unittest

from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Авитоклон' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # register a new account
        r = Role(name='User')
        db.session.add(r)
        db.session.commit()

        response = self.client.post('/auth/registration', data={
            'email': 'email@mail.com',
            'fname': 'Юлик',
            'password': 'supercat',
            'pass_conf': 'supercat',
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/auth/registration', data={
            'email': 'email@mail.com',
            'fname': 'wrongname',
            'password': 'supercat',
            'pass_conf': 'supercat',
        })
        self.assertEqual(response.status_code, 200)
