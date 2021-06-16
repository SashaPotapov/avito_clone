from flask import abort
from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from app.models import User, db, Product

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
        prev_url = url_for('index', page=pagination.prev_num)
        return render_template('index.html', title='Авитоклон', products=products, 
            pagination=pagination, next_url=next_url, prev_url=prev_url)

    @app.route('/product/<int:product_id>')
    def product_page(product_id):
        product = Product.query.filter(Product.id == product_id).first()

        if not product:
            abort(404)
        return render_template('product.html', product=product)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app