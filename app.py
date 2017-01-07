from flask import Flask, send_file, request, redirect, url_for, flash, session
from flask_oauthlib.client import OAuth, OAuthException, OAuthRemoteApp, parse_response
from werkzeug import url_decode
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

@goodreads.tokengetter
def get_goodreads_token(token=None):
	return session.get('goodreads_token')

@app.route('/')
def index():
	return send_file('templates/index.html')

@app.route('/logged_in')
def logged_in():
	return send_file('templates/blah.html')

@app.route('/denied')
def denied():
	return send_file('templates/denied.html')

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