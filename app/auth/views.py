from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from flask_login.utils import login_user, logout_user
from .. import db
from ..models import User
from ..email import send_email
from . import auth
from .forms import LoginForm, RegForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index') 
            return redirect(next)
        flash('Неправильный логин или пароль')
    return render_template('auth/login.html', form=form) 

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы')
    return redirect(url_for('main.index'))

@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    if form.validate_on_submit():
        user = User(email = form.email.data, 
                    name=f'{form.fname.data} {form.lname.data}',
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Подтверждение аккаунта', 'auth/email/confirm', user=user, token=token)
        flash('Ваш аккаунт успешно создан.\nПожалуйста, подтвердите его по ссылке, отправленной на ваш email')
        return redirect(url_for('main.index'))
    return render_template('auth/registration.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('Ваш email уже подтвержден')
    if current_user.confirm(token):
        db.session.commit()
        flash('Email успешно подтвержден')
    else:
        flash('Срок действия подтверждения истек')
        return redirect(url_for('auth.unconfirmed'))
    return redirect(url_for('main.index'))
    
@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        flash('Ваш email уже подтвержден')
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_email_confirmation():
    if current_user.confirmed:
        flash('Ваш email уже подтвержден')
        return redirect(url_for('main.index'))        
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Подтверждение аккаунта', 'auth/email/confirm',\
               user=current_user, token=token)
    return redirect(url_for('main.index'))
