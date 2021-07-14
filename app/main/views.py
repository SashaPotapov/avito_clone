from flask import request, render_template, url_for, abort, redirect, g
from . import main
from .forms import SearchForm, PriceRangeSearchForm
from .. import db
from ..models import Product, User


@main.route('/')
@main.route('/index')
def index():
    search_form = SearchForm()
    range_price_form = PriceRangeSearchForm()
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.published.desc()).paginate(page, error_out=False)
    products = pagination.items
    next_url = url_for('main.index', page=pagination.next_num)
    prev_url = url_for('main.index', page=pagination.prev_num)
    return render_template('main/index.html', title='Авитоклон', products=products, search_form=search_form, range_price_form=range_price_form,
                           pagination=pagination, next_url=next_url, prev_url=prev_url)

@main.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.filter(Product.id == product_id).first()
    user = User.query.filter(User.id == product.user_id).first()
    if not product:
        abort(404)
    return render_template('main/product.html', product=product, user=user)

@main.route('/search')
def search():
    search_form = SearchForm()
    range_price_form = PriceRangeSearchForm()
    if not search_form.validate():
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    products, total = Product.search(search_form.q.data, page, 20)
    next_url = url_for('main.search', q=search_form.q.data, page=page+1) \
        if total > page * 20 else None
    prev_url = url_for('main.search', q=search_form.q.data, page=page-1) \
        if page > 1 else None
    pages = total // 20
    return render_template('main/search.html', title='Поиск', products=products, search_form=search_form, range_price_form=range_price_form,
                           next_url=next_url, prev_url=prev_url, page=page, pages=pages)
    
    
