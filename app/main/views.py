from flask import request, render_template, url_for, abort
from . import main
from .. import db
from ..models import Product

@main.route('/')
@main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.published.desc()).paginate(page, error_out=False)
    products = pagination.items
    next_url = url_for('main.index', page=pagination.next_num)
    prev_url = url_for('main.index', page=pagination.prev_num)
    return render_template('main/index.html', title='Авитоклон', products=products, 
                           pagination=pagination, next_url=next_url, prev_url=prev_url)

@main.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.filter(Product.id == product_id).first()
    if not product:
        abort(404)
    return render_template('main/product.html', product=product)