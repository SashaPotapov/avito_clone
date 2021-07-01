from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import User

class EditProfileForm(FlaskForm):
    picture = FileField('Изменить изображение', validators=[FileAllowed()])
    email = StringField('E-mail', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'class': 'form-control'})
    fname = StringField('Имя', 
        validators=[DataRequired(), Length(2, 64), 
                    Regexp('^[А-Яа-я]+$', 0,
                            'Имя может содержать только буквы русского алфавита.')], render_kw={'class': 'form-control'})
    lname = StringField('Фамилия', validators=[Length(2, 64),
        Regexp('^[А-Яа-я]+$', 0,
                'Фамилия может содержать только буквы русского алфавита.')], render_kw={'class': 'form-control'})
    submit = SubmitField('Изменить', render_kw={'class': 'btn btn-primary'})
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('E-mail уже зарегистрирован')