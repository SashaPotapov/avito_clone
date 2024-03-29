import re
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager
from app.search import add_to_index, query_index, remove_from_index


class SearchableMixin(object):
    @classmethod
    def search(cls, page, per_page, expression, from_num, to_num, order):
        if not from_num:
            from_num = '0'
        if not to_num:
            to_num = '999999'
        ids, total = query_index(
            cls.__tablename__,
            page,
            per_page,
            expression,
            cls.__filterable__,
            from_num,
            to_num,
            order,
        )
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))

        return cls.query.filter(
            cls.id.in_(ids),
        ).order_by(
            db.case(when, value=cls.id),
        ), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def index_update(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return f'<Role {self.name} {self.id}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), nullable=True)
    address = db.Column(db.Text, nullable=True)
    avatar_link = db.Column(db.String(64), nullable=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    products = db.relationship('Product', backref='user')
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            serialised_data = s.loads(token.encode('utf-8'))
        except:
            return False
        if serialised_data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email},
        ).decode('utf-8')

    def confirm_email_change(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            serialised_data = s.loads(token.encode('utf-8'))
        except:
            return False
        if serialised_data.get('change_email') != self.id:
            return False
        new_email = serialised_data.get('new_email')
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def get_avatar_link(self):
        if self.avatar_link:
            return f'/static/profile_image/{self.avatar_link}'
        return '/static/profile_image/default-avatar.jpg'

    @staticmethod
    def check_user(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
            user_id = data.get('confirm')
            return User.query.filter(User.id == user_id).first()
        except:
            return False

    def __repr__(self):
        return f'<User {self.name} {self.id}>'


class Product(SearchableMixin, db.Model):
    __tablename__ = 'products'
    __searchable__ = ['title', 'description', 'price', 'published']
    __filterable__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    avito_id = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(64), nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    link_photo = db.Column(db.String(64), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    category = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hidden = db.Column(db.Boolean, default=False)

    def get_photo_link(self):
        if self.link_photo:
            check_url = re.compile('https:')
            if check_url.search(self.link_photo):
                return self.link_photo

            return f'/static/product_image/{self.link_photo}'
        return '/static/product_image/default-product-image.jpg'

    def comments_count(self):
        return Comment.query.filter(Comment.product_id == self.id).count()

    def __repr__(self):
        return f'<Product {self.title} {self.id}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    product = relationship('Product', backref='comments')
    user = relationship('User', backref='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'
