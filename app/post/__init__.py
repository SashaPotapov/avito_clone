from flask import Blueprint

post = Blueprint('post', __name__, template_folder='post')

from . import views
