# coding: utf-8

from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from . import fb
from flask_oauthlib.client import OAuth
from .. import oauth
from flask_oauth import OAuthException
from .forms import FollowersForm
import facebook
from flask import make_response
from flask.ext.login import login_required

facebook = oauth.remote_app('facebook',
    app_key='FACEBOOK'
)

@fb.before_request
def before_request():
    g.user = None
    if 'facebook_oauth' in session:
        g.user = session['facebook_oauth']

@fb.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if g.user is not None:
        fform = FollowersForm()
	if fform.validate_on_submit():
		url=fform.url_name.data
		q='?ids='+url
		resp = facebook.get(q)
		return render_template('fb/result.html', resp=resp, url=url )
    	return render_template('fb/index.html', fform = fform)


@fb.route('/login')
def login():
    callback = url_for(
        'fb.facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return facebook.authorize(callback=callback)


@fb.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        flash('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))
    	if isinstance(resp, OAuthException):
        	flash('Access denied: %s' % resp.message)

    else:
    	session['facebook_oauth'] = (resp['access_token'], '')
    return redirect(url_for('fb.index'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth')


