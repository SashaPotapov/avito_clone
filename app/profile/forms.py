from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Optional, Email, EqualTo
from wtforms import ValidationError
from ..models import User


class ChangePassForm(FlaskForm):
    password_old = PasswordField('Введите старый пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password_new = PasswordField('Введите новый пароль', validators=[DataRequired(), EqualTo('pass_conf', 
                                                         message='Пароли не совпадают.'), Length(2, 64)], render_kw={'class': 'form-control'})
    pass_conf = PasswordField('Повторите новый пароль', validators=[DataRequired(), Length(2, 64)], render_kw={'class': 'form-control'})
    submit = SubmitField('Изменить', render_kw={'class': 'btn btn-primary'})
    
    
class ChangeNameForm(FlaskForm):
    fname_new = StringField('Введите новое имя', 
        validators=[DataRequired(), Length(2, 64), 
                    Regexp('^[А-Яа-я]+$', 0,
                            'Имя может содержать только буквы русского алфавита.')], render_kw={'class': 'form-control'})
    lname_new = StringField('Введите вашу фамилию (опционально)', validators=[Optional(), Length(2, 64),
        Regexp('^[А-Яа-я]+$', 0,
                'Введите новое имя')], render_kw={'class': 'form-control'})
    submit = SubmitField('Изменить', render_kw={'class': 'btn btn-primary'})
    
    
class ChangeEmailForm(FlaskForm):
    email_new = StringField('E-mail', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'class': 'form-control'})
    submit = SubmitField('Изменить', render_kw={'class': 'btn btn-primary'})
