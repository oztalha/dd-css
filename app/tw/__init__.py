from flask import Blueprint

tw = Blueprint('tw', __name__)

from . import views
