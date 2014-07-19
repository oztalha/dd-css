from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required, Length, Regexp, Optional, NumberRange
from wtforms import ValidationError
from ..models import User


class FollowersForm(Form):
    url_name = StringField('URL Name (e.g. http://www.example.com)',
                validators=[Required()])
    submit = SubmitField('Get Number of Shares')
