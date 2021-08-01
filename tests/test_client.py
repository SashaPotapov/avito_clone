import unittest
from time import sleep

from app import create_app, db
from app.models import Role, User


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
        self.assertTrue('буквы русского алфавита' in response.get_data(
            as_text=True,
        ))

        response = self.client.post(
            '/auth/login',
            data={
                'email': 'wrongemail@mail.com',
                'password': 'supercat',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Неправильный e-mail' in response.get_data(
            as_text=True,
        ))

        response = self.client.post(
            '/auth/login',
            data={
                'email': 'email@mail.com',
                'password': 'supercat',
            })
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            '/auth/unconfirmed',
        )
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(
            '/auth/confirm',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Ссылка на подтверждение' in response.get_data(
            as_text=True,
        ))
        
        user = User.query.filter_by(email='email@mail.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Аккаунт успешно подтвержден' in response.get_data(
            as_text=True,
        ))

        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Ваш e-mail уже подтвержден' in response.get_data(
            as_text=True,
        ))

        response = self.client.get(
            '/auth/unconfirmed',
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            '/auth/confirm',
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            '/auth/logout',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
