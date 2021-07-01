import os
import secrets 
from datetime import datetime
from flask import render_template, redirect, url_for, abort, current_app
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

def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, photo_ext = os.path.splitext(form_photo.filename)
    photo_n = random_hex + photo_ext
    photo_path = os.path.join(current_app.root_path, 'static/product_image/', photo_n)
    form_photo.save(photo_path)
    return photo_n
    
@profile.route('/profile/create_product', methods=['GET', 'POST'])
@login_required
def create_product():   
    form = AddProdForm()
    if form.validate_on_submit():
        prod = Product(title=form.title.data, published=datetime.today().strftime('%d.%m.%Y %H:%M'),
                       price=form.price.data, description=form.description.data, address=form.address.data,
                       category='Электронные книги', user_id=current_user.id)
        db.session.add(prod)
        prod.avito_id = prod.id
        if form.link_photo.data:
            prod.link_photo = save_photo(form.link_photo.data)
        
        db.session.commit()
        return redirect(url_for('profile.user_profile', user_id=current_user.id))
    return render_template('profile/create_product.html', form=form)

@profile.route('/profile/<int:user_id>/user_products')
@login_required
def user_products(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    products = sorted(user.products, reverse=True)
    return render_template('profile/user_products.html', products=products, user=user)
    