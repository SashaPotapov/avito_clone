from datetime import datetime
from flask import render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from flask_user import roles_required
from . import profile
from .forms import AddProdForm
from .. import db
from ..models import User, Product



@profile.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    return render_template('profile/user.html', user=user)

@profile.route('/profile/create_product', methods=['GET', 'POST'])
@login_required
def create_product():   
    form = AddProdForm()
    if form.validate_on_submit():
        prod = Product(title=form.title.data, published=datetime.today().strftime('%d.%m.%Y %H:%M'),
                       price=form.price.data, description=form.description.data, address=form.address.data)
                       #category=form.category.data, link_photo=form.link_photo.data)
        db.session.add(prod)
        prod.avito_id = prod.id
        db.session.commit()
    return render_template('profile/create_product.html', form=form)

@profile.route('/profile/<int:user_id>/user_products')
@login_required
def user_products(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    products = sorted(user.products, reverse=True)
    return render_template('profile/user_products.html', products=products, user=user)
    