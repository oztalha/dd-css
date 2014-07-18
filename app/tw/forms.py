from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import Required, Length, Regexp, Optional, NumberRange
from wtforms import ValidationError
from ..models import User


class FollowersForm(Form):
    screen_name = StringField('Screen Name (e.g. tozCSS)',
                validators=[Required(), Length(1, 15), Regexp('[a-zA-Z0-9_]',
                           0, "Not a valid screen name")])
    followers_limit = IntegerField('Followers Limit (default 5000)',
                    validators=[Optional(),NumberRange(min=1,max=75000,message="Number of followers should be between 1-75000")])
    submit = SubmitField('Get Followers')
