import Flask

app.config['SOCIAL_TWITTER'] = {
    'consumer_key': 'koRF9mYm5CFI17i0NZ7yse3kj',
    'consumer_secret': 'tvjO0G1dxSxFYWxgeAHuZtPv57Vj3sps0nuKBgVhQx2SSkt4Db'
}

# ... other required imports ...
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore

# ... create the app ...

app.config['SECURITY_POST_LOGIN'] = '/profile'

db = SQLAlchemy(app)

# ... define user and role models ...

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)

Security(app, SQLAlchemyUserDatastore(db, User, Role))
Social(app, SQLAlchemyConnectionDatastore(db, Connection))

