from flask import Flask, render_template, request, url_for
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
        page = request.args.get('page', 1, type=int)
        pagination = Product.query.order_by(Product.published.desc()).paginate(page, error_out=False)
        products = pagination.items
        next_url = url_for('index', page=pagination.next_num)
        page = url_for('index', page=pagination.page)
        prev_url = url_for('index', page=pagination.prev_num)
        return render_template('index.html', title='Авитоклон', products=products, 
                                pagination=pagination, next_url=next_url, prev_url=prev_url, page=page)

    return app