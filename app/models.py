from . import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return f'<Role {self.name} {self.id}>'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.Text, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    products = db.relationship('Product', backref='user')

    def __repr__(self):
        return f'<User {self.username} {self.id}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    avito_id = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(64), nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    link_photo = db.Column(db.String(64), nullable=False)
    price = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    category = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Product {self.title} {self.id}>'