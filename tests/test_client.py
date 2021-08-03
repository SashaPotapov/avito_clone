import re
import unittest
from unittest import mock
from datetime import datetime
from time import sleep
from flask_login.utils import login_user, logout_user
from app import create_app, db
from app.models import Product, Role, User


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

    def test_login(self):
        u = User(
            password='supercat',
            email='email@mail.com',
        )
        db.session.add(u)
        db.session.commit()

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

        token = u.generate_confirmation_token(expiration=1)
        sleep(2)
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/auth/unconfirmed')

        token = u.generate_confirmation_token()
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
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

        token = u.generate_confirmation_token()
        u.confirmed = False
        db.session.add(u)
        db.session.commit()
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/auth/login')

        token = u.generate_confirmation_token(expiration=1)
        sleep(2)
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('истекла' in response.get_data(
            as_text=True,
        ))
        self.assertEqual(response.request.path, '/index')

        token = u.generate_confirmation_token()
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/index')    

    def test_product_page(self):
        p = Product(
            title='cat',
            published=datetime.today(),
            price='1000',
            category='cats',
            user_id=1,
        )
        db.session.add(p)
        db.session.commit()
        response = self.client.get(f'/product/{p.id}')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/product/2')
        self.assertEqual(response.status_code, 404)

    @mock.patch('flask_login.utils._get_user')
    def test_profile_page(self, mock_current_user):
        u = User(password='cat', confirmed=True)
        db.session.add(u)
        db.session.commit()
        mock_current_user.return_value = u
        response = self.client.get(f'/profile/{u.id}')
        self.assertEqual(response.status_code, 200)

        p = Product(
            title='cat',
            published=datetime.today(),
            price='1000',
            category='cats',
            user_id=u.id,
        )
        db.session.add(p)
        db.session.commit()

        response = self.client.get(f'/profile/{u.id}/user_products')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/profile/{u.id}/create_product')
        self.assertEqual(response.status_code, 200)