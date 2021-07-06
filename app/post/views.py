import os
import secrets 
from datetime import datetime
from flask import render_template, redirect, url_for, abort, current_app, flash
from flask_login import login_required, current_user
from . import post
from .forms import AddProdForm, EditProdForm
from .. import db
from ..models import User, Product


@post.route('/post/<int:user_id>/user_products')
@login_required
def user_products(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    products = user.products[::-1]
    if current_user != user:
        abort(404)
    return render_template('post/user_products.html', products=products, user=user, title='Объявления ' + user.name)

def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, photo_ext = os.path.splitext(form_photo.filename)
    photo_n = random_hex + photo_ext
    photo_path = os.path.join(current_app.root_path, 'static/product_image/', photo_n)
    form_photo.save(photo_path)
    return photo_n
    
@post.route('/post/<int:user_id>/create_product', methods=['GET', 'POST'])
@login_required
def create_product(user_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    form = AddProdForm()
    if form.validate_on_submit():
        prod = Product(title=form.title.data, published=datetime.today(),
                       price=form.price.data, description=form.description.data, address=form.address.data,
                       category='Электронные книги', user_id=user.id)
        db.session.add(prod)
        prod.avito_id = prod.id
        if form.link_photo.data:
            prod.link_photo = save_photo(form.link_photo.data)
        db.session.commit()
        flash('Объявление успешно добавлено на площадку', 'success')
        return redirect(url_for('post.user_products', user_id=user.id))
    return render_template('post/create_product.html', form=form, title='Создать объявление', user=user)

@post.route('/post/<int:user_id>/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(user_id, product_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    prod = Product.query.filter(Product.id == product_id).first_or_404()
    if current_user != user:
        abort(404)
    form = EditProdForm()
    if form.validate_on_submit():
        prod.title = form.title.data
        prod.price = form.price.data
        prod.description = form.description.data
        prod.address = form.address.data
        
        if form.link_photo.data:
            prod.link_photo = save_photo(form.link_photo.data)

        db.session.add(prod)
        db.session.commit()
        flash('Объявление успешно обновлено', 'success')
        return redirect(url_for('post.user_products', user_id=user.id))
    form.title.data = prod.title
    form.price.data = int(prod.price)
    form.description.data = prod.description
    form.address.data= prod.address
    return render_template('post/edit_product.html', form=form, title='Редактировать объявление', user=user, product=prod)

