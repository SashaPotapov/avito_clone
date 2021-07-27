import os
import secrets

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.email import send_email
from app.models import User

from . import profile
from .forms import (
    ChangeEmailForm, ChangeNameForm,
    ChangePassForm, ChangePhotoForm,
)


@profile.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    return render_template('profile/user.html', user=user)


def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, photo_ext = os.path.splitext(form_photo.filename)
    photo_n = random_hex + photo_ext
    photo_path = os.path.join(
        current_app.root_path,
        'static/profile_image/',
        photo_n,
    )
    form_photo.save(photo_path)
    return photo_n


@profile.route('/profile/<int:user_id>/edit_profile')
@login_required
def edit_profile(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)

    return render_template(
        'profile/edit_profile.html',
        user=user,
        title='Редактировать профиль',
    )


@profile.route(
    '/profile/<int:user_id>/edit_profile/change_password',
    methods=['GET', 'POST'],
)
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
    return render_template(
        'profile/change_password.html',
        form=form,
        user=user,
    )


@profile.route(
    '/profile/<int:user_id>/edit_profile/change_name',
    methods=['GET', 'POST'],
)
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


@profile.route(
    '/profile/<int:user_id>/edit_profile/change_email',
    methods=['GET', 'POST'],
)
@login_required
def change_email(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    form = ChangeEmailForm()
    if form.validate_on_submit():
        email = form.email_new.data
        token = user.generate_email_change_token(email)
        send_email(
            email,
            'Смена email',
            'auth/email/change_email',
            user=user,
            token=token,
        )
        flash_message = (
            'Пожалуйста, подтвердите новый email перейдя по ссылке, '
            + f'отправленной на {email}'
        )
        flash(flash_message, 'info')
    return render_template(
        'profile/change_email.html',
        form=form,
        user=user,
    )


@profile.route('/profile/<int:user_id>/edit_profile/change_email/<token>')
@login_required
def change_email_confirmation(user_id, token):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    if user.confirm_email_change(token):
        db.session.commit()
        flash_message = 'Ваш email успешно обновлен'
        flash(flash_message, 'success')
    else:
        lash_message = (
            'Ссылка на подтверждение истекла. '
            + 'Пожалуйста, отправьте подтверждение еще раз'
        )
        flash(lash_message, 'warning')
    return redirect(url_for('profile.edit_profile', user_id=user.id))


@profile.route(
    '/profile/<int:user_id>/edit_profile/change_photo',
    methods=['GET', 'POST'],
)
@login_required
def change_photo(user_id):
    user = User.query.filter(User.id == user_id).first_or_404()
    if current_user != user:
        abort(404)
    form = ChangePhotoForm()
    if form.validate_on_submit():
        if form.avatar_link.data:
            user.avatar_link = save_photo(form.avatar_link.data)
        db.session.add(user)
        db.session.commit()
        flash('Изображение успешно обновлено', 'success')
    return render_template('profile/change_photo.html', user=user, form=form)
