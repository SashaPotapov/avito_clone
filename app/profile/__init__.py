from flask import Blueprint

profile = Blueprint('profile', __name__, template_folder='profile')

from . import views
