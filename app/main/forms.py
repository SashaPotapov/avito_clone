from flask import request
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.models import Product


class CommentForm(FlaskForm):
    product_id = HiddenField('ID объявления', validators=[DataRequired()])
    comment_text = StringField(
        'Написать комментарий',
        validators=[DataRequired()],
        render_kw={'class': 'form-control'},
    )
    submit = SubmitField('Отправить', render_kw={'class': 'btn btn-primary'})

    def validate_product_id(self, product_id):
        if not Product.query.get(product_id.data):
            raise ValidationError('Такого объявления не существует')


class SearchForm(FlaskForm):
    q = StringField('Поиск')
    from_price = StringField('От')
    to_price = StringField('До, руб.')
    order = SelectField(
        'Сортировка',
        choices=[
            (('published', 'desc'), 'Дата по убыванию'),
            (('published', 'asc'), 'Дата по возрастанию'),
            (('price', 'asc'), 'Цена по возрастанию'),
            (('price', 'desc'), 'Цена по убыванию'),
        ])
    submit = SubmitField('Подтвердить')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super().__init__(*args, **kwargs)
