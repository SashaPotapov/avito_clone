from flask import request, render_template, url_for
from . import main
from .. import db
from ..models import Product

@main.route('/')
@main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.published.desc()).paginate(page, error_out=False)
    products = pagination.items
    next_url = url_for('.index', page=pagination.next_num)
    page = url_for('.index', page=pagination.page)
    prev_url = url_for('.index', page=pagination.prev_num)
    return render_template('main/index.html', title='Авитоклон', products=products, 
                            pagination=pagination, next_url=next_url, prev_url=prev_url, page=page)