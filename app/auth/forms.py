from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'class': 'form-control'})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    remember_me = BooleanField('Оставаться в системе')
    submit = SubmitField('Подтвердить', render_kw={'class': 'btn btn-primary'})

class RegForm(FlaskForm):
    email = StringField('E-mail*', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'class': 'form-control'})
    fname = StringField('Введите ваше имя, которое будет видно другим пользователям*', 
        validators=[DataRequired(), Length(2, 64), 
                    Regexp('^[А-Яа-я]+$', 0,
                            'Имя может содержать только буквы русского алфавита.')])
    lname = StringField('Введите вашу фамилию (опционально)', validators=[Optional(), Length(2, 64),
        Regexp('^[А-Яа-я]+$', 0,
                'Фамилия может содержать только буквы русского алфавита.')], render_kw={'class': 'form-control'})
    password = PasswordField('Введите пароль*', validators=[DataRequired(), Length(8, 64)], render_kw={'class': 'form-control'})
    pass_conf = PasswordField('Повторите пароль*', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают.')], render_kw={'class': 'form-control'})
    submit = SubmitField('Зарегистрироваться', render_kw={'class': 'btn btn-primary'})
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('E-mail уже зарегистрирован')
    
class ChangePassForm(FlaskForm):
    password_old = PasswordField('Введите старый пароль', validators=[DataRequired()])
    password_new = PasswordField('Введите новый пароль', validators=[DataRequired(), EqualTo('pass_conf', 
                                                         message='Пароли не совпадают.'), Length(2, 64)])
    pass_conf = PasswordField('Повторите новый пароль', validators=[DataRequired(), Length(2, 64)])
    submit = SubmitField('Сменить пароль')
    
class ChangeNameForm(FlaskForm):
    fname_new = StringField('Введите новое имя', 
        validators=[DataRequired(), Length(2, 64), 
                    Regexp('^[А-Яа-я]+$', 0,
                            'Имя может содержать только буквы русского алфавита.')])
    lname_new = StringField('Введите вашу фамилию (опционально)', validators=[Optional(), Length(2, 64),
        Regexp('^[А-Яа-я]+$', 0,
                'Введите новое имя')])
    submit = SubmitField('Сменить имя')
    
    
class ChangeEmailForm(FlaskForm):
    email_new = StringField('E-mail', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Сменить email')
    