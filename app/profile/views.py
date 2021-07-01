from itertools import product
from flask import render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from flask_user import roles_required
from . import profile
from .. import db
from ..models import User, Product
from .forms import EditProfileForm


@profile.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    return render_template('profile/user.html', user=user)

@profile.route('/profile/<int:user_id>/user_products')
@login_required
def user_products(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    products = sorted(user.products, reverse=True)
    return render_template('profile/user_products.html', products=products, user=user)

@profile.route('/profile/<int:user_id>/edit_profile')
@login_required
def edit_user_info(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    form = EditProfileForm()
    if form.validate_on_submit():
        