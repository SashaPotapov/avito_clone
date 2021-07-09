from flask import request, render_template, url_for, abort, flash, redirect
from flask_login import current_user
from . import main
from .. import db
from ..models import Product, User, Comment
from .forms import CommentForm

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
    user = User.query.filter(User.id == product.user_id).first()

    if not product:
        abort(404)
    
    comment_form = CommentForm(product_id=product.id)
    return render_template('main/product.html', product=product, user=user, form=comment_form)

@main.route('/product/comment', methods=['POST'])
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        if Product.query.filter(Product.id == form.product_id.data).first():
            comment = Comment(
                            text=form.comment_text.data,
                            product_id=form.product_id.data,
                            user_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий успешно добавлен', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в заполнении поля "{getattr(form, field).label.text}": - {error}', 'warning')
    return redirect(request.referrer)
            