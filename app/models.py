from flask_sqlalchemy import SQLAlchemy
from app import db

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    link_photo = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Item {self.name} {self.id}>'
