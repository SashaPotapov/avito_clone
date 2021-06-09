from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        return 'Hello!'

    return app