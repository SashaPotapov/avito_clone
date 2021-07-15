from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    q = StringField('Поиск')
    from_price = StringField('От')
    to_price = StringField('До, руб.')
    order = SelectField('Сортировка', choices=[('', 'По умолчанию'), ('published_asc', 'Дата по возрастанию'), ('published_desc', 'Дата по убыванию'),
                                               ('price_asc', 'Цена по возрастанию'), ('price_desc', 'Цена по убыванию')])
    submit = SubmitField('Подтвердить')
    
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
        