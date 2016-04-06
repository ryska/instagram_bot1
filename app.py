import bottle
import beaker.middleware
from collections import Counter
import pynstagram
from bottle import route, redirect, post, run, request, hook
from instagram import client, subscriptions


bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

CONFIG = {
    'client_id': '7da4a6bf233f41ccb5f3e9a444217951',
    'client_secret': '512f10cd05524dce9a25a21d5fed181a',
    'redirect_uri': 'http://localhost:8515/oauth_callback'
}

unauthenticated_api = client.InstagramAPI(**CONFIG)


@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


def process_tag_update(update):
    print(update)

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)


@route('/')
def home():
    try:
        # zmienilem tutaj na public_content, to jest potrzebne do szukania po tagach
        url = unauthenticated_api.get_authorize_url(scope=["public_content"])
        return '<a href="%s">Connect with Instagram</a>' % url
    except Exception as e:
        print(e)


def get_nav():
    nav_menu = ("<h1>Python Instagram</h1>"
                "<ul>"
                    "<li><a href='/tag_search'>Tags</a> Search for tags, view tag info and get media by tag</li>"
                    "<li><a href='/upload'>Upload</a> Upload pic</li>"
                "</ul>"
                )
    return nav_menu

@route('/upload')
def upload():
    with pynstagram.client('urbanshot__', 'kluza1') as client:
        client.upload('pic1.jpg', '#meow')
        return "<p>Uploaded!</p>"
upload()

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
    return get_nav()


@route('/tag_search')
def tag_search():
    access_token = request.session['access_token']
    familiar_tags = []          #lista tagow, ktore sa w opisach znalezionych zdjec
    current_tag = "friends"     #tag, po ktorym odbywa sie wyszukiwanie
    content = "<h2>Tag Search</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        tag_search, next_tag = api.tag_search(q=current_tag)
        tag_recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name)
        photos = []
        for tag_media in tag_recent_media:
            photos.append('<img src="%s"/>' % tag_media.get_standard_resolution_url() )
            photos.append('</br>%s' % tag_media.caption.text )

            #petla wyszukujaca w opisie tagow i dodajaca je do listy
            for tag in get_tags(tag_media.caption.text):
                familiar_tags.append(tag)

        #Counter - funkcja zaimportowana z collections; tworzy krotki (element_listy, liczba_wystapien)
        familiar_tags = Counter(familiar_tags).most_common()
        content += ''.join(photos)
        content += "</br></br>Current tag: %s" % current_tag
        content += "</br>%s" % familiar_tags
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/realtime_callback')
@post('/realtime_callback')
def on_realtime_callback():
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


def get_tags(caption):
    current_tag = ""
    tag_list = []
    tag_found = False

    for item in caption:
        if( item == '#' ):
            tag_found = True

        elif( item != '#' and item != ' ' and tag_found == True):
            current_tag += item

        elif( item == ' ' and tag_found == True):
            tag_list.append(current_tag)
            current_tag = ""
            tag_found = False

    if( current_tag != "" and tag_found == True ):
        tag_list.append(current_tag)

    return tag_list

bottle.run(app=app, host='localhost', port=8515, reloader=True)