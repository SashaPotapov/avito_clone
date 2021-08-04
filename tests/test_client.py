import io
import os
import unittest
from datetime import datetime
from time import sleep
from unittest import mock

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
        
        # test registration with wrong name
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

        # test login with wrong name
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

        # test expired token when authenticated
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

        # test confirmation when not authenticated
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

        # test expired token when not authenticated
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

        # test successful confirmation when not authenticated
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
        self.assertTrue(p.title in response.get_data(
            as_text=True,
        ))

        response = self.client.get('/product/2')
        self.assertEqual(response.status_code, 404)

    @mock.patch('flask_login.utils._get_user')
    def test_profile_page(self, mock_current_user):
        u = User(password='supercat', confirmed=True)
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
        self.assertTrue(p.title in response.get_data(
            as_text=True,
        ))

        response = self.client.get(f'/profile/{u.id}/edit_profile')
        self.assertEqual(response.status_code, 200)

        u2 = User(password='supercat', confirmed=True)
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(f'/profile/{u2.id}/edit_profile')
        self.assertEqual(response.status_code, 404)
        
        
        response = self.client.post(
            f'/profile/{u.id}/edit_profile/change_password',
            data={
                'password_old': 'supercat',
                'password_new': 'newsupercat',
                'pass_conf': 'newsupercat',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(u.verify_password('newsupercat'))

        response = self.client.post(
            f'/profile/{u.id}/edit_profile/change_password',
            data={
                'password_old': 'supercat',
                'password_new': 'newsupercat',
                'pass_conf': 'newsupercat',
            })
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/profile/{u2.id}/edit_profile/change_password',
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            f'/profile/{u.id}/edit_profile/change_name',
            data={
                'fname_new': 'новоеимя',
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(u.name, 'новоеимя')

        response = self.client.post(
            f'/profile/{u.id}/edit_profile/change_name',
            data={
                'fname_new': 'wrongname',
            })
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/profile/{u2.id}/edit_profile/change_name',
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            f'/profile/{u.id}/edit_profile/change_email',
            data={
                'email_new': 'newemail@mail.com',
            })
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/profile/{u2.id}/edit_profile/change_email',
        )
        self.assertEqual(response.status_code, 404)

        token = u.generate_email_change_token('newemail@mail.com')
        response = self.client.get(
            f'/profile/{u.id}/edit_profile/change_email/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u.email, 'newemail@mail.com')

        token = u.generate_email_change_token('newemail@mail.com')
        response = self.client.get(
            f'/profile/{u.id}/edit_profile/change_email/{token}',
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f'/profile/{u2.id}/edit_profile/change_email/{token}',
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            f'/profile/{u.id}/edit_profile/change_photo',
            data={
                'avatar_link': (io.BytesIO(b'abcdef'), 'test.jpg'),
            },
            follow_redirects=True,
            content_type='multipart/form-data',
        )
        self.assertEqual(response.status_code, 200)
        path = f'{self.app.root_path}/static/profile_image'
        self.assertTrue(u.avatar_link in os.listdir(path))
        os.remove(f'{path}/{u.avatar_link}')

        response = self.client.get(
            f'/profile/{u2.id}/edit_profile/change_photo',
        )
        self.assertEqual(response.status_code, 404)
        
    @mock.patch('flask_login.utils._get_user')
    def test_create_product(self, mock_current_user):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        mock_current_user.return_value = u

        response = self.client.post(
            f'/profile/{u.id}/create_product',
            data={
                'title': 'title',
                'price': '100',
                'description': 'description',
                'address': 'address',
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('подтвердите аккаунт' in response.get_data(
            as_text=True,
        ))

        u.confirmed = True
        db.session.add(u)
        db.session.commit()
        response = self.client.post(
            f'/profile/{u.id}/create_product',
            data={
                'title': 'title',
                'price': '100',
                'description': 'description',
                'address': 'address',
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('title' in response.get_data(
            as_text=True,
        ))

        p = Product.query.filter(Product.title == 'title').first()
        response = self.client.get(f'/product/{p.id}')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            f'/profile/{u.id}/create_product',
            data={
                'title': '',
                'price': '100',
                'description': 'description',
                'address': 'address',
            })
        self.assertEqual(response.status_code, 200)

        u2 = User(password='cat', confirmed=True)
        db.session.add(u2)
        db.session.commit()
        mock_current_user.return_value = u2
        response = self.client.post(
            f'/profile/{u.id}/create_product',
            data={
                'title': 'title',
                'price': '100',
                'description': 'description',
                'address': 'address',
            })
        self.assertEqual(response.status_code, 404)

    @mock.patch('flask_login.utils._get_user')
    def test_edit_product(self, mock_current_user):
        u = User(password='cat', confirmed=True)
        db.session.add(u)
        db.session.commit()
        p = Product(
            title='title',
            published=datetime.today(),
            price='1000',
            description='description',
            category='cats',
            user_id=u.id,
        )
        db.session.add(p)
        db.session.commit()
        mock_current_user.return_value = u

        response = self.client.get(f'/profile/{u.id}/edit_product/{p.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('title' in response.get_data(
            as_text=True,
        ))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('title' in response.get_data(as_text=True))

        data = {
            'title': 'newtitle',
            'price': '100',
            'description': 'description',
            'address': 'address',
        }
        data['link_photo'] = (io.BytesIO(b'abcdef'), 'test.jpg')
        response = self.client.post(
            f'/profile/{u.id}/edit_product/{p.id}',
            data=data,
            follow_redirects=True,
            content_type='multipart/form-data',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('newtitle' in response.get_data(
            as_text=True,
        ))
        path = f'{self.app.root_path}/static/product_image'
        self.assertTrue(p.link_photo in os.listdir(path))
        os.remove(f'{path}/{p.link_photo}')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('newtitle' in response.get_data(as_text=True))

        u2 = User(password='cat', confirmed=True)
        db.session.add(u2)
        db.session.commit()
        mock_current_user.return_value = u2
        response = self.client.get(f'/profile/{u.id}/edit_product/{p.id}')
        self.assertEqual(response.status_code, 404)

        mock_current_user.return_value = u
        response = self.client.post(f'/profile/{u.id}/hide_product/{p.id}')
        self.assertEqual(response.status_code, 302)

        mock_current_user.return_value = u2
        response = self.client.get(f'/profile/{u.id}/hide_product/{p.id}')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse('newtitle' in response.get_data(as_text=True))

        mock_current_user.return_value = u
        response = self.client.post(f'/profile/{u.id}/show_product/{p.id}')
        self.assertEqual(response.status_code, 302)

        mock_current_user.return_value = u2
        response = self.client.get(f'/profile/{u.id}/show_product/{p.id}')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('newtitle' in response.get_data(as_text=True))

        mock_current_user.return_value = u2
        response = self.client.get(f'/profile/{u.id}/delete_product/{p.id}')
        self.assertEqual(response.status_code, 404)

        mock_current_user.return_value = u
        response = self.client.post(f'/profile/{u.id}/delete_product/{p.id}')
        self.assertEqual(response.status_code, 302)
        p = Product.query.filter(Product.title == 'newtitle').first()
        self.assertFalse(p)

    @mock.patch('app.main.views.get_redirect_target')
    @mock.patch('flask_login.utils._get_user')
    def test_comments(self, mock_current_user, mock_redirect_target):
        u = User(password='cat', confirmed=True)
        db.session.add(u)
        db.session.commit()
        p = Product(
            title='title',
            published=datetime.today(),
            price='1000',
            description='description',
            category='cats',
            user_id=u.id,
        )
        db.session.add(p)
        db.session.commit()
        mock_current_user.return_value = u
        mock_redirect_target.return_value = '/'

        response = self.client.post(
            '/product/comment',
            data={
                'comment_text': 'comment',
                'product_id': p.id,
            }, follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/product/{p.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comment' in response.get_data(
            as_text=True,
        ))

        response = self.client.post(
            '/product/comment',
            data={
                'comment_text': '',
                'product_id': p.id,
            }, follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('field is required' in response.get_data(
            as_text=True,
        ))
