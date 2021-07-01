from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Optional
from wtforms import ValidationError
from ..models import User

class AddProdForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired(), Length(1, 64)], render_kw={'class': 'form-control'})
    price = DecimalField('Цена', validators=[DataRequired(), Length(1, 64)], render_kw={'class': 'form-control'})
    description = TextAreaField('Описание (опционально)', validators=[Optional()], render_kw={'class': 'form-control'})
    address = StringField('Адрес (опционально)', validators=[Optional(), Length(1, 64)], render_kw={'class': 'form-control'})
    link_photo = FileField('Загрузите изображение товара', validators=[FileAllowed(['jpg', 'png'])], render_kw={'class': 'form-control-file'})
    # category
    submit = SubmitField('Добавить товар', render_kw={'class': 'btn btn-primary'})