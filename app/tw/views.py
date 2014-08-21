# coding: utf-8

from flask import Flask, make_response
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask.ext.login import login_required
from flask.ext.login import current_user
from . import tw
from .. import oauth
from .forms import FollowersForm, UserTimelineForm
import twitter as t
import json
from functools import partial
import sys
import csv
import io
from collections import defaultdict
from bson.json_util import dumps
from datetime import datetime
from ..util import save_to_mongo
import time
from threading import Thread
from flask import copy_current_request_context

twitter = oauth.remote_app(    
     'twitter',
     app_key='TWITTER'
)

@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@tw.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@tw.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('tw/index.html')



@tw.route('/user-timeline', methods=['GET', 'POST'])
@login_required
def user_timeline():
    tweets = None
    if g.user is not None:
        form = UserTimelineForm()
        if form.validate_on_submit():
            flash("Your request is received, you can download the results here when its completed")
            
            @copy_current_request_context
            def harvest_user_timeline_async(screen_name,max_results):
            	twitter_api = oauth_login()
            	harvest_user_timeline(twitter_api,screen_name=screen_name,max_results=int(max_results))
            
            thr = Thread(target=harvest_user_timeline_async, args=[form.screen_name.data, form.max_results.data])
            thr.start()
            return redirect(url_for('main.user', username=current_user.username))
    return render_template('tw/user-timeline.html', form=form)


def harvest_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=1000):
     
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"    
    
    ff = defaultdict()
    ff['qname'] = 'Twitter User Timeline'
    ff['created_time'] = datetime.now()
    ff['username'] = current_user.username
    ff['parameters'] = defaultdict()
    ff['parameters']['screen_name'] = screen_name if screen_name else user_id
    ff['parameters']['max_results'] = max_results
    ff['data'] = defaultdict(list)


    kw = {  # Keyword args for the Twitter API call
        'count': 200,
        'trim_user': 'true',
        'include_rts' : 'true',
        'since_id' : 1
        }
    
    if screen_name:
        kw['screen_name'] = screen_name
    else:
        kw['user_id'] = user_id
        
    max_pages = 16
    results = []
    
    tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
    
    if tweets is None: # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []
        
    results += tweets
    
    print >> sys.stderr, 'Fetched %i tweets' % len(tweets)
    
    page_num = 1
    
    # Many Twitter accounts have fewer than 200 tweets so you don't want to enter
    # the loop and waste a precious request if max_results = 200.
    
    # Note: Analogous optimizations could be applied inside the loop to try and 
    # save requests. e.g. Don't make a third request if you have 287 tweets out of 
    # a possible 400 tweets after your second request. Twitter does do some 
    # post-filtering on censored and deleted tweets out of batches of 'count', though,
    # so you can't strictly check for the number of results being 200. You might get
    # back 198, for example, and still have many more tweets to go. If you have the
    # total number of tweets for an account (by GET /users/lookup/), then you could 
    # simply use this value as a guide.
    
    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry
    
    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:
    
        # Necessary for traversing the timeline in Twitter's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.
        kw['max_id'] = min([ tweet['id'] for tweet in tweets]) - 1 
    
        tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
        results += tweets
        ff['data'] = results
        id = save_to_mongo(ff,"ddcss","queries")

        print >> sys.stderr, 'Fetched %i tweets' % (len(tweets),)
    
        page_num += 1
        
    print >> sys.stderr, 'Done fetching tweets'
    return results[:max_results]
    


@tw.route('/friends-followers', methods=['GET', 'POST'])
@login_required
def friends_followers():
    tweets = None
    if g.user is not None:
        form = FollowersForm()
        if form.validate_on_submit():
            flash("Your request is received, you can download the results here when its completed")
            
            @copy_current_request_context
            def getFollowers_async(screen_name,friends_limit,followers_limit):
                    getFollowers(screen_name,friends_limit,followers_limit)

            thr = Thread(target=getFollowers_async, args=[form.screen_name.data, form.friends_limit.data, form.followers_limit.data])
            thr.start()
            #res = getFollowers(form.screen_name.data, form.friends_limit.data, form.followers_limit.data)
            return redirect(url_for('main.user', username=current_user.username))
            #response = make_response(res)
            #response.headers["Content-Disposition"] = "attachment; filename=followers.csv"
            #return response #return redirect(request.args.get('next') or url_for('tw.index'))
    return render_template('tw/friends-followers.html', form=form)


@tw.route('/login')
@login_required
def login():
    if g.user is not None:
        return redirect(url_for('tw.index'))
    callback_url = url_for('tw.oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@tw.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('tw.index'))


@tw.route('/oauthorized')
@twitter.authorized_handler
def oauthorized(resp):
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('tw.index'))


def oauth_login():
    tok,tos = get_twitter_token()
    auth = t.oauth.OAuth(tok, tos, twitter.consumer_key, twitter.consumer_secret)
    twitter_api = t.Twitter(auth=auth)
    return twitter_api


def getFollowers(screen_name,friends_limit,followers_limit):
    if int(friends_limit) == 0 and int(followers_limit) == 0:
        flash('At least one of the limits should be greater than zero')
        return redirect(url_for('tw.friends_followers'))
    twitter_api = oauth_login()
    friends_ids, followers_ids = get_friends_followers_ids(twitter_api, screen_name=screen_name, friends_limit=int(friends_limit), followers_limit=int(followers_limit))


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
    
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except t.api.TwitterHTTPError, e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise


def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=1000, followers_limit=1000):
    
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"
    
    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters
    
    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids, 
                              count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids, 
                                count=5000)

    friends_ids, followers_ids = [], []
    #ddcss.queries.ensureIndex( { username: 1 } )
    ff = defaultdict()
    ff['qname'] = 'Twitter Friends & Followers'
    ff['created_time'] = datetime.now()
    ff['username'] = current_user.username
    ff['parameters'] = defaultdict()
    ff['parameters']['screen_name'] = screen_name if screen_name else user_id
    ff['parameters']['friends_limit'] = friends_limit
    ff['parameters']['followers_limit'] = followers_limit
    ff['data'] = defaultdict(list)

    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"], 
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:
        
        if limit == 0: continue
        
        cursor = -1
        while cursor != 0:
        
            # Use make_twitter_request via the partially bound callable...
            if screen_name: 
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']
        
            print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids), 
                                                    label, (user_id or screen_name))
        
            # XXX: You may want to store data during each iteration to provide an 
            # an additional layer of protection from exceptional circumstances
            ff['data'][label] = ids
            #save_json("ff",ff)
            print "ids size"
            print len(ids)
            id = save_to_mongo(ff,"ddcss","queries")
            #mongo_reloaded = load_from_mongo("ddcss","queries")
            #print mongo_reloaded
            #print dumps(mongo_reloaded, ensure_ascii=False)
        
            if len(ids) >= limit or response is None:
                break

    # Do something useful with the IDs, like store them to disk...
    return friends_ids[:friends_limit], followers_ids[:followers_limit]



def get_followers_ids(twitter_api, screen_name=None, user_id=None, followers_limit=5000):
    
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"
    
    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters
    
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids, 
                                count=5000)

    followers_ids = []
    
    for twitter_api_func, limit, ids, label in [ 
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:
        
        if limit == 0: continue
        
        cursor = -1
        while cursor != 0:
        
            # Use make_twitter_request via the partially bound callable...
            if screen_name: 
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']
        
            print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids), 
                                                    label, (user_id or screen_name))
        
            # XXX: You may want to store data during each iteration to provide an 
            # an additional layer of protection from exceptional circumstances
        
            if len(ids) >= limit or response is None:
                break

    # Do something useful with the IDs, like store them to disk...
    return followers_ids[:followers_limit]


