from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired('Необходимо заполнить поле'), Length(1, 64), Email('Введите корректный e-mail')], render_kw={'class': 'form-control'})
    password = PasswordField('Пароль', validators=[DataRequired('Необходимо заполнить поле')], render_kw={'class': 'form-control'})
    remember_me = BooleanField('Оставаться в системе')
    submit = SubmitField('Подтвердить', render_kw={'class': 'btn btn-primary'})

class RegForm(FlaskForm):
    email = StringField('E-mail*', validators=[DataRequired('Необходимо заполнить поле'), Length(1, 64), Email('Введите корректный e-mail')], render_kw={'class': 'form-control'})
    fname = StringField('Введите ваше имя, которое будет видно другим пользователям*', 
        validators=[DataRequired('Необходимо заполнить поле'), Length(2, 64), 
                    Regexp('^[А-Яа-я]+$', 0,
                            'Имя может содержать только буквы русского алфавита.')], render_kw={'class': 'form-control'})
    lname = StringField('Введите вашу фамилию (опционально)', validators=[Optional(), Length(2, 64),
        Regexp('^[А-Яа-я]+$', 0,
                'Фамилия может содержать только буквы русского алфавита.')], render_kw={'class': 'form-control'})
    password = PasswordField('Введите пароль*', validators=[DataRequired('Необходимо заполнить поле'), Length(8, 64)], render_kw={'class': 'form-control'})
    pass_conf = PasswordField('Повторите пароль*', validators=[DataRequired('Необходимо заполнить поле'), EqualTo('password', message='Пароли не совпадают.')], 
                              render_kw={'class': 'form-control'})
    submit = SubmitField('Зарегистрироваться', render_kw={'class': 'btn btn-primary'})
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('E-mail уже зарегистрирован')