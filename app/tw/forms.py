from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, RadioField
from wtforms.validators import Required, Length, Regexp, Optional, NumberRange
from wtforms import ValidationError
from ..models import User


class FollowersForm(Form):
    screen_name = StringField('Screen Name (e.g. tozCSS)',
                validators=[Required(), Length(1, 15), Regexp('[a-zA-Z0-9_]',
                           0, "Not a valid screen name")])
    friends_limit = IntegerField('Friends Limit (default 0)', default = 0,
                    validators=[Optional(),NumberRange(min=0,max=75000,message="Number of followers should be between 0-75000")])
    followers_limit = IntegerField('Followers Limit (default 1000)',  default = 1000,
                    validators=[Optional(),NumberRange(min=0,max=75000,message="Number of followers should be between 0-75000")])
    submit = SubmitField('Get Friends and/or Followers')
