from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.models import Product


class CommentForm(FlaskForm):
    product_id = HiddenField('ID объявления', validators=[DataRequired()])
    comment_text = StringField('Написать комментарий', 
                                validators=[DataRequired()], 
                                render_kw={"class": "form-control"})
    submit = SubmitField('Отправить',render_kw={"class": "btn btn-primary"})

    def validate_product_id(self, product_id):
        if not Product.query.get(product_id.data):
            raise ValidationError('Такого объявления не существует')
