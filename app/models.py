import re
from flask import url_for
from flask_login import UserMixin
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db, login_manager

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
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def confirm_email_change(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
    
    def get_avatar_link(self):
        if self.avatar_link:
            return url_for('static', filename='profile_image/' + self.avatar_link)
        return url_for('static', filename='profile_image/' + 'default-avatar.jpg')
    
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

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    avito_id = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(64), nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    link_photo = db.Column(db.String(64), nullable=True)
    price = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    category = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hidden = db.Column(db.Boolean, default=False)
    
    def get_photo_link(self):
        if self.link_photo:
            check_url = re.compile(r'https:')
            if check_url.search(self.link_photo):
                return self.link_photo 
            return url_for('static', filename='product_image/' + self.link_photo)
        return url_for('static', filename='product_image/' + 'default-product-image.jpg')

    def __repr__(self):
        return f'<Product {self.title} {self.id}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))