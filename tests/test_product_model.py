import unittest
from datetime import datetime

from app import create_app, db
from app.models import Product, Comment


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

    def test_get_photo_link_default(self):
        p = Product(
            title='cat',
            published=datetime.today(),
            price='1000',
            category='cats',
        )
        db.session.add(p)
        db.session.commit()
        link = p.get_photo_link()
        self.assertTrue(
            link == '/static/product_image/default-product-image.jpg',
        )

    def test_get_photo_link(self):
        p = Product(
            title='cat',
            published=datetime.today(),
            price='1000',
            category='cats',
        )
        p.link_photo = 'link.jpg'
        db.session.add(p)
        db.session.commit()
        link = p.get_photo_link()
        self.assertTrue(link == '/static/product_image/link.jpg')

    def test_get_photo_outside_link(self):
        p = Product(
            title='cat',
            published=datetime.today(),
            price='1000',
            category='cats',
        )
        p.link_photo = 'https://link.jpg'
        db.session.add(p)
        db.session.commit()
        link = p.get_photo_link()
        self.assertTrue(link == 'https://link.jpg')

    def test_comments_count(self):
        p = Product(
            title='cat',
            published=datetime.today(),
            price='1000',
            category='cats',
        )
        db.session.add(p)
        db.session.commit()

        com = Comment(text='text', product_id=p.id)
        com2 = Comment(text='text', product_id=p.id)
        db.session.add(com)
        db.session.add(com2)
        db.session.commit()
        self.assertTrue(p.comments_count() == 2)
