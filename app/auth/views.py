from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required
from flask_login.utils import login_user, logout_user
from . import auth
from .. import db
from .forms import LoginForm, RegForm
from ..models import User

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
    flash('Вы разлогинились из системы')
    return redirect(url_for('main.index'))

@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, 
                    name=f'{form.fname.data} {form.lname.data}',
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Теперь вы можете войти в систему')
        return redirect(url_for('auth.login'))
    return render_template('auth/registration.html', form=form)