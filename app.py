import web
import bottle
import beaker.middleware
import urllib
import requests
from collections import Counter
import pynstagram
import pic_manager
from pic_manager import cut_image, upload
from tag_manager import search_tag
from six.moves import urllib
# from insta_manager import realtime_callback
from bottle import route, redirect, get, post, run, request, hook, template, SimpleTemplate, static_file
from instagram import client, subscriptions
from config import CONFIG, unauthenticated_api
from PIL import Image
import sys
import os



bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)



@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


def process_tag_update(update):
    print(update)

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@route('/')
def home():
    try:
        # zmienilem tutaj na public_content, to jest potrzebne do szukania po tagach
        url = unauthenticated_api.get_authorize_url(scope=["public_content","comments","likes","follower_list","basic","relationships"])
        return template('index', url=url)
        # return '<p>connect rhr fhsfgjnz</p>'
    except Exception as e:
        print(e)




@route('/upload')
def on_upload():
    list = ["f4f", 'like4like']
    upload(list)
    return template('upload.html')


@route('/oauth_callback')
def on_callback():
    code = request.GET.get("code")
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        request.session['access_token'] = access_token
    except Exception as e:
        print(e)
    return template('nav_menu')

@route('/tag_search')
def on_tag_search():
    page = urllib.request.urlopen('http://websta.me/hot')
    content = page.read()
    splitted_content = content.split('<a href="/tag/', 100)
    tag_lists = []

    for tag_cell in splitted_content[1:]:
        splitted_tag = tag_cell.split('">#', 1)
        tag_lists.append(splitted_tag[0])
    # return tag_lists
    return template('data', tag_lists=tag_lists)

@route('/realtime_callback')
@post('/realtime_callback')
def on_realtime_callback():
    reactor = subscriptions.SubscriptionsReactor()
    reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)

    mode = request.GET.get("hub.mode")
    challenge = request.GET.get("hub.challenge")
    verify_token = request.GET.get("hub.verify_token")
    if challenge:
        return challenge
    else:
        x_hub_signature = request.header.get('X-Hub-Signature')
        raw_response = request.body.read()
        try:
            reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
        except subscriptions.SubscriptionVerifyError:
            print("Signature mismatch")


bottle.run(app=app, host='localhost', port=8515, reloader=True)