from flask import Markup, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_login.utils import login_user, logout_user

from app import db
from app.email import send_email
from app.models import Role, User

from . import auth
from .forms import LoginForm, RegForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user and user.verify_password(form.password.data):
            if not user.confirmed:
                flash_message = (
                    'Ваш аккаунт не подтвержден.'
                    + f'<a href="{url_for("auth.unconfirmed")}'
                    + 'class="alert-link">'
                    + 'Отправить подтверждение еще раз.</a>'
                )

                flash(Markup(flash_message), 'warning')
            login_user(user, remember=form.remember_me.data)
            next_url = request.args.get('next')

            if next_url is None or not next_url.startswith('/'):
                next_url = url_for('main.index')
            flash('Вы успешно вошли в систему', 'success')
            return redirect(next_url)

        flash('Неправильный e-mail или пароль', 'warning')
    return render_template('auth/login.html', form=form, title='Авторизация')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    next_url = request.args.get('next')
    if next_url is None or not next_url.startswith('/'):
        next_url = url_for('main.index')
    flash('Вы успешно вышли из системы', 'info')
    return redirect(next_url)


@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            name=form.fname.data + form.lname.data,
            password=form.password.data,
            role_id=Role.query.filter_by(name='User').first().id,
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Подтверждение аккаунта',
            'auth/email/confirm',
            user=user,
            token=token,
        )
        flash_message = (
            'Ваш аккаунт успешно создан.'
            + 'Пожалуйста, подтвердите его по ссылке, '
            + f'отправленной на {user.email}'
        )
        flash(flash_message, 'success')
        return redirect(url_for('main.index'))

    return render_template(
        'auth/registration.html',
        form=form,
        title='Регистрация',
    )


@auth.route('/confirm/<token>')
def confirm(token):
    user = User.check_user(token)
    if user:
        if user.confirmed:
            flash('Ваш e-mail уже подтвержден', 'info')
            if current_user.is_authenticated:
                return redirect(url_for(
                    'profile.user_profile',
                    user_id=user.id,
                ))

            return redirect(url_for('main.index'))

        if user.confirm(token):
            db.session.commit()
            if current_user.is_authenticated:
                flash('Аккаунт успешно подтвержден.', 'success')
                return redirect(url_for(
                    'profile.user_profile',
                    user_id=user.id,
                ))

            flash(
                'Аккаунт успешно подтвержден. Теперь вы можете войти.',
                'success',
            )
            return redirect(url_for('auth.login'))

    elif current_user.is_authenticated:
        return redirect(url_for('auth.unconfirmed'))

    flash_message = (
        'Ссылка на подтверждение истекла.'
        + 'Пожалуйста, залогиньтесь и отправьте подтверждение еще раз'
    )
    flash(flash_message, 'warning')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        flash('Ваш e-mail уже подтвержден', 'info')
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_email_confirmation():
    if current_user.confirmed:
        flash('Ваш e-mail уже подтвержден', 'info')
        return redirect(url_for('main.index'))

    flash_message = (
        'Ссылка на подтверждение аккаунта'
        + f'отправлена на {current_user.email}'
    )
    flash(flash_message, 'success')
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        'Подтверждение аккаунта',
        'auth/email/confirm',
        user=current_user,
        token=token,
    )
    return redirect(url_for('main.index'))
