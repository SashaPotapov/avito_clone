from app.utils import get_redirect_target
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Comment, Product, User

from . import main
from .forms import CommentForm, SearchForm


@main.route('/')
@main.route('/index')
def index():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(
        Product.published.desc(),
    ).paginate(page, error_out=False)
    products = pagination.items
    return render_template(
        'main/index.html',
        title='Авитоклон',
        products=products,
        search_form=search_form,
        pagination=pagination,
        next_url=url_for('main.index', page=pagination.next_num),
        prev_url=url_for('main.index', page=pagination.prev_num),
    )


@main.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.filter(Product.id == product_id).first()
    user = User.query.filter(User.id == product.user_id).first()

    if not product:
        abort(404)
    comment_form = CommentForm(product_id=product.id)
    return render_template(
        'main/product.html',
        product=product,
        user=user,
        form=comment_form,
    )


@main.route('/product/comment', methods=['POST'])
@login_required
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            text=form.comment_text.data,
            product_id=form.product_id.data,
            user_id=current_user.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий успешно добавлен', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f"""
                    Ошибка в заполнении поля
                     "{getattr(form, field).label.text}": - {error}
                    """, 'warning',
                )
    return redirect(get_redirect_target())


@main.route('/search')
def search():
    search_form = SearchForm()
    if not search_form.validate():
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    order = (
        search_form.order.data.split('_')[0],
        search_form.order.data.split('_')[1],
    )

    products, total = Product.search(
        page,
        20,  # Items on the page
        search_form.q.data,
        search_form.from_price.data,
        search_form.to_price.data,
        order,
    )
    next_url = url_for(
        'main.search',
        q=search_form.q.data,
        from_price=search_form.from_price.data,
        to_price=search_form.to_price.data,
        order=search_form.order.data,
        page=page + 1,
    ) if total > page * 20 else None

    prev_url = url_for(
        'main.search',
        q=search_form.q.data,
        from_price=search_form.from_price.data,
        to_price=search_form.to_price.data,
        order=search_form.order.data,
        page=page - 1,
    ) if page > 1 else None

    pages = total // 20
    return render_template(
        'main/search.html',
        title='Поиск',
        products=products,
        search_form=search_form,
        next_url=next_url,
        prev_url=prev_url,
        page=page,
        pages=pages,
    )
