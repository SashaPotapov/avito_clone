from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Оставаться в системе')
    submit = SubmitField('Подтвердить')