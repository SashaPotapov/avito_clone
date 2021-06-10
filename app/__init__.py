from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from app.models import db, Product

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    bootstrap = Bootstrap(app) 

    @app.route('/')
    @app.route('/index')
    def index():
        products = Product.query.order_by(Product.published.desc()).all()
        return render_template('index.html', title='Авито', products=products)

    return app