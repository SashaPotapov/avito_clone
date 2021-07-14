from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    q = StringField('Поиск', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
        
class PriceRangeSearchForm(FlaskForm):
    from_p = StringField('От', validators=[DataRequired()])
    to_p = StringField('До', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
    
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(PriceRangeSearchForm, self).__init__(*args, **kwargs)
    
