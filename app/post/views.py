import os
import secrets 
from datetime import datetime
from flask import render_template, redirect, url_for, abort, current_app, flash, request
from flask_login import login_required, current_user
from . import post
from .forms import AddProdForm, EditProdForm
from .. import db
from ..models import User, Product


@post.route('/profile/<int:user_id>/user_products')
@login_required
def user_products(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.filter(Product.user_id==user.id).order_by(Product.published.desc()).paginate(page, error_out=False, per_page=5)
    products = pagination.items
    next_url = url_for('post.user_products', user_id=user.id, page=pagination.next_num)
    prev_url = url_for('post.user_products', user_id=user.id, page=pagination.prev_num)
    return render_template('post/user_products.html', products=products, user=user, title='Объявления ' + user.name,
                            next_url=next_url, prev_url=prev_url, pagination=pagination)

def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, photo_ext = os.path.splitext(form_photo.filename)
    photo_n = random_hex + photo_ext
    photo_path = os.path.join(current_app.root_path, 'static/product_image/', photo_n)
    form_photo.save(photo_path)
    return photo_n
    
@post.route('/profile/<int:user_id>/create_product', methods=['GET', 'POST'])
@login_required
def create_product(user_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    if not user.confirmed:
        flash('Пожалуйста, подтвердите аккаунт, чтобы добавить объявление', 'warning')
        next = request.args.get('next')
        if next is None:
            next = url_for('main.index') 
        return redirect(next)
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

@post.route('/profile/<int:user_id>/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(user_id, product_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    prod = Product.query.filter(Product.id == product_id).first_or_404()
    if current_user != user or current_user.id != prod.user_id:
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
        next = request.args.get('next')
        if next is None:
            next = url_for('post.user_products', user_id=user.id)
        flash('Объявление успешно обновлено', 'success')
        return redirect(next)
    form.title.data = prod.title
    form.price.data = int(prod.price)
    form.description.data = prod.description
    form.address.data= prod.address
    return render_template('post/edit_product.html', form=form, title='Редактировать объявление', user=user, product=prod)

@post.route('/profile/<int:user_id>/hide_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def hide_product(user_id, product_id): 
    user = User.query.filter(User.id == user_id).first_or_404()
    prod = Product.query.filter(Product.id == product_id).first_or_404()
    if current_user != user or current_user.id != prod.user_id:
        abort(404)
    prod.hidden = True
    db.session.add(prod)
    db.session.commit()
    flash('Объявление скрыто из общего поиска', 'success')
    return redirect(url_for('post.user_products', user_id=user.id))

@post.route('/profile/<int:user_id>/show_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def show_product(user_id, product_id): 
    user = User.query.filter(User.id == user_id).first_or_404()
    prod = Product.query.filter(Product.id == product_id).first_or_404()
    if current_user != user or current_user.id != prod.user_id:
        abort(404)
    prod.hidden = False
    db.session.add(prod)
    db.session.commit()
    flash('Объявление снова доступно всем', 'success')
    return redirect(url_for('post.user_products', user_id=user.id))

@post.route('/profile/<int:user_id>/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(user_id, product_id): 
    user = User.query.filter(User.id == user_id).first_or_404()
    prod = Product.query.filter(Product.id == product_id).first_or_404()
    if current_user != user or current_user.id != prod.user_id:
        abort(404)
    db.session.delete(prod)
    db.session.commit()
    flash('Объявление удалено', 'warning')
    return redirect(url_for('post.user_products', user_id=user.id))
