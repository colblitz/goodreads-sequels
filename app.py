from flask import Flask, send_file, request, redirect, url_for, flash, session
from flask_oauthlib.client import OAuth, OAuthException, OAuthRemoteApp, parse_response
from werkzeug import url_decode
import oauth2 as oldOauth

import time
import random


import config

app = Flask(__name__)
app.secret_key = "blah"

oauth = OAuth(app)

class GoodreadsOAuthRemoteApp(OAuthRemoteApp):
	def __init__(self, *args, **kwargs):
		super(GoodreadsOAuthRemoteApp, self).__init__(*args, **kwargs)

	def handle_unknown_response(self):
		print "handle_unknown_response"

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



		# print "\nresponse: ", response
		# print "\ncontent: ", content
		# print "\n"
		# data = parse_response(response, content)



		# print "data: ", data

		# if response['status'] != '200':
		# 	raise OAuthException(
		# 		'Invalid response from %s' % self.name,
		# 		type='invalid_response', data=data
		# 	)

		# return data
		# if self.access_token_method != 'POST':
	 #        raise OAuthException(
	 #            'Unsupported access_token_method: %s' %
	 #            self.access_token_method
	 #        )

		# client = self.make_client()
		# remote_args = {
		#     'code': request.args.get('code'),
		#     'client_secret': self.consumer_secret,
		#     'redirect_uri': session.get('%s_oauthredir' % self.name)
		# }
		# # remote_args.update(self.access_token_params)

		# # reddit_basic_auth = base64.encodestring('%s:%s' % (REDDIT_APP_ID, REDDIT_APP_SECRET)).replace('\n', '')
		# body = client.prepare_request_body(**remote_args)
		# while True:
		#     resp, content = self.http_request(
		#         self.expand_url(self.access_token_url),
		#         headers={'Content-Type': 'application/x-www-form-urlencoded'},
		#         # headers={'Content-Type': 'application/x-www-form-urlencoded',
		#         #          'Authorization': 'Basic %s' % reddit_basic_auth,
		#         #          'User-Agent': REDDIT_USER_AGENT},
		#         data=to_bytes(body, self.encoding),
		#         method=self.access_token_method,
		#     )
		#     # Reddit API is rate-limited, so if we get 429, we need to retry
		#     if resp.code != 429:
		#         break
		#     time.sleep(1)

		# data = parse_response(resp, content, content_type=self.content_type)
		# if resp.code not in (200, 201):
		#     raise OAuthException(
		#         'Invalid response from %s' % self.name,
		#         type='invalid_response', data=data
		#     )
		# return data








#     	token = session['%s_oauthtok' % self.name]
#     	print "token: ", token

#     	response, content = client.request(self.access_token_url, 'POST')

#     	 # def request(self, uri, method="GET", body=b'', headers=None,
#       #   redirections=httplib2.DEFAULT_MAX_REDIRECTS, connection_type=None):
#         # DEFAULT_POST_CONTENT_TYPE = 'application/x-www-form-urlencoded'

#         self = token/consumer
#         # uri = self.access_token_url
#         # method = 'POST'
#         # body = b''
#         headers = None
#         redirections=httplib2.DEFAULT_MAX_REDIRECTS
#         connection_type=None

#         # if not isinstance(headers, dict):
#         #     headers = {}

#         # if method == "POST":
#         #     headers['Content-Type'] = headers.get('Content-Type',
#         #         DEFAULT_POST_CONTENT_TYPE)

#         # is_form_encoded = \
#         #     headers.get('Content-Type') == 'application/x-www-form-urlencoded'

#         # if is_form_encoded and body:
#         #     parameters = parse_qs(body)
#         # else:
#         #     parameters = None
#         headers['Content-Type'] = 'application/x-www-form-urlencoded'
#         parameters = None

#         # req = Request.from_consumer_and_token(self.consumer,
#         #     token=self.token, http_method=method, http_url=uri,
#         #     parameters=parameters, body=body, is_form_encoded=is_form_encoded)

#         parameters = {
#             'oauth_consumer_key': self.consumer_key,
#             'oauth_timestamp': str(int(time.time())),
#             'oauth_nonce': str(random.SystemRandom().randint(0, 100000000)),
#             'oauth_version': "1.0",
#             'oauth_token': token[0]
#         }
#         # return cls(http_method, http_url, parameters, body=body,
#         #     is_form_encoded=is_form_encoded)
#         return cls('POST', self.access_token_url, parameters, body=b'',
#             is_form_encoded=true)

#         if url is not None:
#         self.url = to_unicode(self.access_token_url)
#         self.method = 'POST'
#         # if parameters is not None:
#         #     for k, v in parameters.items():
#         #         k = to_unicode(k)
#         #         v = to_unicode_optional_iterator(v)
#         #         self[k] = v
#         self.body = b''
#         self.is_form_encoded = True





# SignatureMethod_HMAC_SHA1()



#         req.sign_request(self.method, self.consumer, self.token)

#         self['oauth_signature_method'] = signature_method.name
#         self['oauth_signature'] = signature_method.sign(self, consumer, token)



#         scheme, netloc, path, params, query, fragment = urlparse(uri)
#         realm = urlunparse((scheme, netloc, '', None, None, None))

#         if is_form_encoded:
#             body = req.to_postdata()
#         elif method == "GET":
#             uri = req.to_url()
#         else:
#             headers.update(req.to_header(realm=realm))

#         return httplib2.Http.request(self, uri, method=method, body=body,
#             headers=headers, redirections=redirections,
#             connection_type=connection_type)












#     	headers['Content-Type'] = 'application/x-www-form-urlencoded'

#     	parameters = None
#     	req = Request.from_consumer_and_token(self.consumer,
#             token=self.token, http_method='Post', http_url=self.access_token_url,
#             parameters=None, body=body, is_form_encoded=true)




#     	def from_consumer_and_token(cls, consumer, token=None,
#             http_method=HTTP_METHOD, http_url=None, parameters=None,
#             body=b'', is_form_encoded=False):

#         parameters = {
#             'oauth_consumer_key': self.consumer_key,
#             'oauth_timestamp': str(int(time.time())),
#             'oauth_nonce': str(random.SystemRandom().randint(0, 100000000)),
#             'oauth_version': "2.0",
#             'oauth_token': token[0]
#         }

#         # if token:
#         #     parameters['oauth_token'] = token.key
#         #     if token.verifier:
#         #         parameters['oauth_verifier'] = token.verifier

#         return cls(http_method, http_url, parameters, body=body,
#             is_form_encoded=is_form_encoded)
#             def __init__(self, method=HTTP_METHOD, url=None, parameters=None,
#                  body=b'', is_form_encoded=False):
#         if url is not None:
#             self.url = to_unicode(url)
#         self.method = method
#         if parameters is not None:
#             for k, v in parameters.items():
#                 k = to_unicode(k)
#                 v = to_unicode_optional_iterator(v)
#                 self[k] = v
#         self.body = body
#         self.is_form_encoded = is_form_encoded










#     	token = oauth.Token(request_token['oauth_token'],
#                     request_token['oauth_token_secret'])

# 		client = oauth.Client(consumer, token)
# 		response, content = client.request(access_token_url, 'POST')


#     	print "Goodreads handle unknown response"
#     	print "session:"
#     	print session
#     	return None
#     	# self.http_request(
#     	# 	self.access_token_url,

#     	# )



	 #    if self.access_token_method != 'POST':
	 #        raise OAuthException(
	 #            'Unsupported access_token_method: %s' %
	 #            self.access_token_method
	 #        )

	 #    client = self.make_client()
	 #    remote_args = {
	 #        'code': request.args.get('code'),
	 #        'client_secret': self.consumer_secret,
	 #        'redirect_uri': session.get('%s_oauthredir' % self.name)
	 #    }
	 #    remote_args.update(self.access_token_params)

	 #    reddit_basic_auth = base64.encodestring('%s:%s' % (REDDIT_APP_ID, REDDIT_APP_SECRET)).replace('\n', '')
	 #    body = client.prepare_request_body(**remote_args)
	 #    while True:
	 #        resp, content = self.http_request(
	 #            self.expand_url(self.access_token_url),
	 #            headers={'Content-Type': 'application/x-www-form-urlencoded',
	 #                     'Authorization': 'Basic %s' % reddit_basic_auth,
	 #                     'User-Agent': REDDIT_USER_AGENT},
	 #            data=to_bytes(body, self.encoding),
	 #            method=self.access_token_method,
	 #        )
	 #        # Reddit API is rate-limited, so if we get 429, we need to retry
	 #        if resp.code != 429:
	 #            break
	 #        time.sleep(1)

	 #    data = parse_response(resp, content, content_type=self.content_type)
	 #    if resp.code not in (200, 201):
	 #        raise OAuthException(
	 #            'Invalid response from %s' % self.name,
	 #            type='invalid_response', data=data
	 #        )
	 #    return data




goodreads = GoodreadsOAuthRemoteApp(oauth, 'goodreads',
	base_url='https://www.goodreads.com',
	request_token_url='http://www.goodreads.com/oauth/request_token',
	authorize_url='http://www.goodreads.com/oauth/authorize',
	access_token_url='http://www.goodreads.com/oauth/access_token',
	consumer_key=config.goodreadsKey,
	consumer_secret=config.goodreadsSecret)

@goodreads.tokengetter
def get_goodreads_token(token=None):
	print "get_goodreads_token"
	print session.get('goodreads_oauthtok')
	return session.get('goodreads_token')

@app.route('/')
def index():
	return send_file('templates/index.html')

@app.route('/logged_in')
def logged_in():
	return send_file('templates/blah.html')

@app.route('/login')
def login():
	print "login"
	return goodreads.authorize(callback=url_for('oauth_authorized',
		next=request.args.get('next') or request.referrer or None))




# @app.route('/oauth_authorized')
# def oauth_authorized():
# 	print "------------------------"
# 	print "request\n"
# 	print request
# 	print ""
# 	print request.args
# 	print request.headers
# 	print "\nresp\n"
# 	print resp

# 	next_url = request.args.get('next') or url_for('index')
# 	print next_url

# 	token = request.args.get('oauth_token')
# 	authorize = request.args.get('authorize')
# 	if token:
# 		print "have token: ", token

# 	if authorize == 0:
# 		print "denied request to sign in"
# 		return redirect(next_url)

# 	# session['goodreads_token'] = (
# 	# 	token,
# 	# 	resp['oauth_token_secret']
# 	# )
# 	# session['goodreads_user'] = resp['screen_name']

# 	# flash('You were signed in as %s' % resp['screen_name'])
# 	return redirect(next_url)

@app.route('/oauth_authorized')
def oauth_authorized():
	print "---------- oauth_authorized"
	print "request:\n"
	print request

	next_url = request.args.get('next') or url_for('index')
	resp = goodreads.authorized_response()
	print "\nresponse:\n"
	print resp

	print "\nsession:\n"
	print session

	if resp is None:
		print "Denied request"
		flash(u'You denied the request to sign in.')
		return redirect(next_url)

	session['goodreads_token'] = (
		resp['oauth_token'],
		resp['oauth_token_secret']
	)
	# session['twitter_user'] = resp['screen_name']

	return redirect(url_for('logged_in'))