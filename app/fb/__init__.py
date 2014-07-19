from flask import Blueprint

fb = Blueprint('fb', __name__)

from . import views
