from flask import render_template, redirect, url_for, abort
from flask_login import login_required
from . import profile
from .. import db
from ..models import User, Product


@profile.route('/profile/<int: user_id>')
@login_required
def user_profile(user_id):
    user = User.query.filter(User.id == user_id).first()
    products = user.products.order_by(Product.published.desc()).all()
    if not user:
        abort(404)
    return render_template('profile/user.html', user=user, products=products)
