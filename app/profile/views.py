import os
import secrets 
from flask import render_template, redirect, url_for, abort, current_app, flash
from flask_login import login_required, current_user
from flask_user import roles_required
from . import profile
from .forms import ChangePassForm, ChangeEmailForm, ChangeNameForm
from .. import db
from ..email import send_email
from ..models import User, Product


@profile.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):   
    user = User.query.filter(User.id == user_id).first_or_404()
    return render_template('profile/user.html', user=user, title=user.name)

def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, photo_ext = os.path.splitext(form_photo.filename)
    photo_n = random_hex + photo_ext
    photo_path = os.path.join(current_app.root_path, 'static/profile_image/', photo_n)
    form_photo.save(photo_path)
    return photo_n
    
@profile.route('/profile/<int:user_id>/edit_profile')
@login_required
def edit_profile(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    return render_template('profile/edit_profile.html', user=user)

@profile.route('/profile/<int:user_id>/edit_profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    form = ChangePassForm()
    if form.validate_on_submit():
        if user.verify_password(form.password_old.data):
            user.password = form.password_new.data
            db.session.add(user)
            db.session.commit()
            flash('Ваш пароль успешно обновлен', 'success')
            return redirect(url_for('profile.edit_profile', user_id=user.id))
        else:
            flash('Неверный пароль')
    return render_template('profile/change_password.html', form=form, user=user)

@profile.route('/profile/<int:user_id>/edit_profile/change-name', methods=['GET', 'POST'])
@login_required
def change_name(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    form = ChangeNameForm()
    if form.validate_on_submit():
        user.name = f'{form.fname_new.data} {form.lname_new.data}'
        db.session.add(user)
        db.session.commit()
        flash('Ваше имя успешно обновлено', 'success')
        return redirect(url_for('profile.edit_profile', user_id=user.id))
    return render_template('profile/change_name.html', form=form, user=user)

@profile.route('/profile/<int:user_id>/edit_profile/change-email', methods=['GET', 'POST'])
@login_required
def change_email(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    form = ChangeEmailForm()
    if form.validate_on_submit():
        email = form.email_new.data
        token = user.generate_email_change_token(email)
        send_email(email, 'Смена email', 'auth/email/change_email',\
                   user=user, token=token)
        flash(f'Пожалуйста, подтвердите новый email перейдя по ссылке, отправленной на {email}', 'info')
    return render_template('profile/change_email.html', form=form, user=user)       

@profile.route('/profile/<int:user_id>/edit_profile/change-email/<token>')
@login_required
def change_email_confirmation(user_id, token):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    if user.confirm_email_change(token):
        db.session.commit()
        flash('Ваш email успешно обновлен', 'success')
    else:
        flash('Ссылка на подтверждение истекла. Пожалуйста, отправьте подтверждение еще раз', 'warning')
    return redirect(url_for('main.index'))

