from flask import Flask, send_file, request, redirect, url_for, flash, session, render_template
from flask_oauthlib.client import OAuth, OAuthException, OAuthRemoteApp, parse_response
from werkzeug import url_decode

from xml.etree.ElementTree import ElementTree

import oauth2 as oldOauth

import config

app = Flask(__name__)
app.secret_key = "blah"

oauth = OAuth(app)

class GoodreadsOAuthRemoteApp(OAuthRemoteApp):
	def __init__(self, *args, **kwargs):
		super(GoodreadsOAuthRemoteApp, self).__init__(*args, **kwargs)

	def handle_unknown_response(self):
		if request.args.get('authorize') == 0:
			return None

		consumer = oldOauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
		client = oldOauth.Client(consumer, oldOauth.Token(*session['%s_oauthtok' % self.name]))
		response, content = client.request(self.access_token_url, 'POST')

		if response['status'] not in ('200', '201'):
			raise OAuthException(
				'Invalid response from %s' % self.name,
				type='invalid_response', data=response)

		decoded = url_decode(content).to_dict()
		return decoded

goodreads = GoodreadsOAuthRemoteApp(oauth, 'goodreads',
	base_url='https://www.goodreads.com',
	request_token_url='http://www.goodreads.com/oauth/request_token',
	authorize_url='http://www.goodreads.com/oauth/authorize',
	access_token_url='http://www.goodreads.com/oauth/access_token',
	consumer_key=config.goodreadsKey,
	consumer_secret=config.goodreadsSecret)

def elementtree_to_dict(element):
    node = dict()

    text = getattr(element, 'text', None)
    if text is not None:
        node['text'] = text

    node.update(element.items()) # element's attributes

    child_nodes = {}
    for child in element: # element's children
        child_nodes.setdefault(child, []).append( elementtree_to_dict(child) )

    # convert all single-element lists into non-lists
    for key, value in child_nodes.items():
        if len(value) == 1:
             child_nodes[key] = value[0]

    node.update(child_nodes.items())

    return node

@goodreads.tokengetter
def get_goodreads_token(token=None):
	return session.get('goodreads_token')

@app.route('/')
@app.route("/index")
def index():
	if session['goodreads_token']:
		print 'still have token'
		return redirect(url_for('logged_in'))
	return render_template('index.html', message="Hasdfi.")

@app.route('/logged_in')
def logged_in():
	print "logged in"
	if not session['goodreads_token']:
		print "going to index"
		return redirect(url_for('index'))

	print "request user"
	resp = goodreads.get('/api/auth_user')
	userId = resp.data.find('user').get('id')
	username = resp.data.find('user/name').text

	shelves = goodreads.get('/shelf/list.xml', data = {
		'key': config.goodreadsKey,
		'user_id': userId,
	})

	shelfItems = map(lambda x: {
		'name': x.find('name').text,
		'count': int(x.find('book_count').text)
	}, shelves.data.findall("./shelves/user_shelf"))

	return render_template('index.html', message="Look at your shelves", shelfItems=shelfItems)

@app.route('/sequelize', methods=['POST'])
def sequelize():
	print request.json['name']
	return render_template('index.html', message='Sequelizing')

@app.route('/denied')
def denied():
	return render_template('index.html', message="Maybe next time o/")

@app.route('/login')
def login():
	return goodreads.authorize(callback=url_for('oauth_authorized',
		next=request.args.get('next') or request.referrer or None))


@app.route('/oauth_authorized')
def oauth_authorized():
	next_url = request.args.get('next') or url_for('index')
	resp = goodreads.authorized_response()

	if resp is None:
		return redirect(url_for('denied'))

	session['goodreads_token'] = (
		resp['oauth_token'],
		resp['oauth_token_secret']
	)

	return redirect(url_for('logged_in'))