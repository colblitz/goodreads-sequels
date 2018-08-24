from flask import Flask, send_file, request, redirect, url_for, flash, session, render_template, g
from flask_oauthlib.client import OAuth, OAuthException, OAuthRemoteApp, parse_response
from werkzeug import url_decode

import oauth2 as oldOauth
import os
import sqlite3
import re

from datetime import date

import config

app = Flask(__name__)
app.secret_key = "blah"

oauth = OAuth(app)

####################
# Database Interface

DATABASE=os.path.join(app.root_path, 'database.db')

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
		db.row_factory = sqlite3.Row
	return db

def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

print "Checking for database:"
if not os.path.isfile(DATABASE):
	print "db not found, creating"
	init_db()

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

# create table books (
#   bookId integer primary key not null,
#   workId integer
# );
# create table works (
#   workId integer primary key not null,
#   bestBookId integer,
#   seriesId integer,
#   position integer,
#   publicationDate integer,
#   lastChecked integer
# );
# create table series (
#   seriesId integer primary key not null,
#   lastChecked integer
# );

def joinInts(l):
	return ",".join(str(x) for x in l)

def newWorkDict():
	return {
		"workId": None,
		"workName": None,
		"bookImageUrl": None,
		"bestBookId": None,
		"seriesId": None,
		"position": None,
		"publicationDate": None,
		"lastChecked": None
	}

def bookDictToTuple(d):
	return (d["bookId"], d["workId"])

def workDictToTuple(d):
	return (d["workId"], d["workName"], d["bookImageUrl"], d["bestBookId"], d["seriesId"], d["position"], d["publicationDate"], d["lastChecked"])

def seriesDictToTuple(d):
	return (d["seriesId"], d["seriesName"], d["lastChecked"])

def getBooksToWorks(bookIds):
	bookToWork = {}
	for row in query_db("SELECT * FROM books JOIN works ON books.workId = works.workId WHERE bookId IN (%s)" % joinInts(bookIds)):
		bookToWork[row['bookId']] = row['workId']
	return bookToWork

def getPossibleNewSeries(workIds):
	# Get best book ids of the works we haven't checked in a while
	cutoff = date.today().toordinal() - 7
	booksToQuery = set()
	for row in query_db("SELECT bestBookId FROM works WHERE workId IN (%s) AND lastChecked < %s" % (joinInts(workIds), cutoff)):
		booksToQuery.add(row['bestBookId'])
	return booksToQuery

def getReadInformation(workIds):
	print "get read information"
	unpublished = set()
	readInSeries = {} # seriesId -> latest position
	for row in query_db("SELECT * FROM works WHERE workId IN (%s)" % joinInts(workIds)):
		print row, row['seriesId']
		if not row['publicationDate']:
			unpublished.add(row['bestBookId'])
		if row['seriesId']:
			if row['seriesId'] not in readInSeries:
				readInSeries[row['seriesId']] = row['position']
			else:
				readInSeries[row['seriesId']] = max(readInSeries[row['seriesId']], row['position'])
	return unpublished, readInSeries

def getSeriesNames(seriesIds):
	seriesNames = {}
	for row in query_db("SELECT * FROM series WHERE seriesId IN (%s)" % (joinInts(seriesIds))):
		seriesNames[row['seriesId']] = row['seriesName']
	return seriesNames

def getSeriesToQuery(seriesIds):
	# Remove ids that are in table and up-to-date
	cutoff = date.today().toordinal() - 7
	seriesToQuery = set(seriesIds)
	for row in query_db("SELECT seriesId FROM series WHERE seriesId IN (%s) AND lastChecked > %s" % (joinInts(seriesIds), cutoff)):
		seriesToQuery.remove(row['seriesId'])
	return seriesToQuery

def getBooksToAdd(readInSeries):
	bestBookIds = {}
	for row in query_db("SELECT * FROM works WHERE seriesId IN (%s) ORDER BY position ASC" % joinInts(readInSeries.keys())):
		if row['seriesId'] not in bestBookIds:
			bestBookIds[row['seriesId']] = []
		if row['position'] >= readInSeries[row['seriesId']]:
			bestBookIds[row['seriesId']].append(row)
	return bestBookIds

	# bestBookIds = set()
	# for row in query_db("SELECT * FROM works WHERE seriesId IN (%s)" % joinInts(readInSeries.keys())):
	# 	if row['position'] > readInSeries[row['seriesId']]:
	# 		bestBookIds.add(row['bestBookId'])
	# return bestBookIds

def insertBookRows(bookDicts):
	bookTuples = map(lambda x: bookDictToTuple(x), bookDicts)
	get_db().cursor().executemany("INSERT OR REPLACE INTO books VALUES (?,?)", bookTuples)
	get_db().commit()

def insertWorkRows(workDicts):
	workTuples = map(lambda x: workDictToTuple(x), workDicts)
	get_db().cursor().executemany("INSERT OR REPLACE INTO works VALUES (?,?,?,?,?,?,?,?)", workTuples)
	get_db().commit()

def insertSeriesRows(seriesDicts):
	seriesTuples = map(lambda x: seriesDictToTuple(x), seriesDicts)
	get_db().cursor().executemany("INSERT OR REPLACE INTO series VALUES (?,?,?)", seriesTuples)
	get_db().commit()

#######################
# Goodreads OAuth class

class GoodreadsOAuthRemoteApp(OAuthRemoteApp):
	def __init__(self, *args, **kwargs):
		super(GoodreadsOAuthRemoteApp, self).__init__(*args, **kwargs)

	def handle_unknown_response(self):
		if request.args.get('authorize') == 0:
			return None

		print "lkjalskdjflkjasdf"
		consumer = oldOauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
		client = oldOauth.Client(consumer, oldOauth.Token(*session['%s_oauthtok' % self.name]))
		response, content = client.request(self.access_token_url, 'POST')

		print response

		if response['status'] not in ('200', '201'):
			raise OAuthException(
				'Invalid response from %s' % self.name,
				type='invalid_response', data=response)

		decoded = url_decode(content).to_dict()
		return decoded

goodreads = GoodreadsOAuthRemoteApp(oauth, 'goodreads',
	base_url='https://www.goodreads.com',
	request_token_url='https://www.goodreads.com/oauth/request_token',
	authorize_url='https://www.goodreads.com/oauth/authorize',
	access_token_url='https://www.goodreads.com/oauth/access_token',
	consumer_key=config.goodreadsKey,
	consumer_secret=config.goodreadsSecret)

@goodreads.tokengetter
def get_goodreads_token(token=None):
	return session.get('goodreads_token')

def safeStrip(s):
	if s:
		return s.strip()
	return s

####
# Util things
def getAllBooksFromShelf(name, count):
	allBookIds = []
	page = 1
	while len(allBookIds) < count:
		print "requesting page ", page
		books = goodreads.get('/review/list', data = {
			'v': 2,
			'id': session['goodreads_user_id'],
			'shelf': request.json['name'],
			'key': config.goodreadsKey,
			'per_page': 200,
			'page': page,
			'format': 'xml'
		}).data.find("reviews")

		bookIds = map(lambda x: int(x.text), books.findall("./review/book/id"))
		allBookIds.extend(bookIds)

		if books.get('end') == books.get('total'):
			break
		page += 1

	return allBookIds

def getWorkPublication(node):
	try:
		pYearT = node.find("work/original_publication_year").text
		pMonthT = node.find("work/original_publication_month").text
		pDayT = node.find("work/original_publication_day").text

		pYear = int(pYearT) if pYearT else None
		pMonth = int(pMonthT) if pMonthT else 1
		pDay = int(pDayT) if pDayT else 1

		if (pYear):
			return date(pYear, pMonth, pDay).toordinal()
		else:
			return None
	except:
		print "Error parsing publication date: ", pYearT, pMonthT, pDayT

def parsePosition(text):
	try:
		# collections: "1-2", "3-6", etc.
		if "-" in text:
			return 0
		# if it has a note: "3.5 (incl.1.5 & 2.5)"
		return float(text.split(" ")[0])
	except:
		print "Error parsing position: ", text
		return 0

# def parseTitle(text):
# 	if text:
# 		return text.strip()
# 	return "Untitled"

def parseTitle(work, bestBook):
	workTitle = work.find("original_title").text
	if workTitle:
		return workTitle.strip()
	bestBookTitle = bestBook.find("title").text
	if bestBookTitle:
		return re.sub(r'\([^)]*\)', '', bestBookTitle).strip()
	return "Untitled"

def getBookInfo(bookId):
	print "get book info: ", bookId
	bookInfo = goodreads.get('/book/show/' + str(bookId), data = {
		'format': 'xml',
		'key': config.goodreadsKey
	}).data.find("book")

	workId = int(bookInfo.find("work/id").text)
	bookDict = { "bookId": bookId, "workId": workId }

	workDict = newWorkDict()

	print "----------- ", bookId
	print bookInfo
	print bookInfo.find("work/original_title").text
	print bookInfo.find("image_url").text

	workDict["workId"] = workId
	workDict["workName"] = parseTitle(bookInfo.find("work"), bookInfo)
	workDict["bookImageUrl"] = safeStrip(bookInfo.find("image_url").text)
	workDict["bestBookId"] = int(bookInfo.find("work/best_book_id").text)
	workDict["lastChecked"] = date.today().toordinal()

	pDate = getWorkPublication(bookInfo)
	if (pDate):
		workDict["publicationDate"] = pDate

	seriesWork = bookInfo.find("series_works/series_work")
	if (seriesWork):
		workDict["seriesId"] = int(seriesWork.find("series/id").text)
		workDict["position"] = parsePosition(seriesWork.find("user_position").text)
	return bookDict, workDict

def processNewBooks(bookIds):
	bookDicts = []
	workDicts = []
	workIds = set()
	for bookId in bookIds:
		bookDict, workDict = getBookInfo(bookId)
		bookDicts.append(bookDict)
		workDicts.append(workDict)
		workIds.add(bookDict['workId'])
	insertBookRows(bookDicts)
	insertWorkRows(workDicts)
	return workIds

def seriesWorkToWorkRow(sw, seriesId):
	workDict = newWorkDict()
	workDict["workId"] = int(sw.find("work/id").text)
	workDict["workName"] = parseTitle(sw.find("work"), sw.find("work/best_book"))
	workDict["bookImageUrl"] = safeStrip(sw.find("work/best_book/image_url").text)
	workDict["bestBookId"] = int(sw.find("work/best_book/id").text)
	workDict["lastChecked"] = date.today().toordinal()

	pDate = getWorkPublication(sw)
	if (pDate):
		workDict["publicationDate"] = pDate

	workDict["seriesId"] = seriesId
	workDict["position"] = parsePosition(sw.find("user_position").text)
	return workDict

def getSeriesInfo(seriesId):
	print "get series info: ", seriesId
	seriesInfo = goodreads.get('/series/' + str(seriesId), data = {
		'format': 'xml',
		'key': config.goodreadsKey
	}).data.find("series")
	# laksjdlfjalsdjlfkj
	seriesName = seriesInfo.find("title").text.strip()
	print "seriesName: ", seriesName
	seriesDict = {"seriesId": seriesId, "seriesName": seriesName, "lastChecked": date.today().toordinal() }
	workDicts = map(lambda sw: seriesWorkToWorkRow(sw, seriesId), seriesInfo.findall("./series_works/series_work"))
	return workDicts, seriesDict

def processSeries(seriesIds):
	allWorkDicts = []
	seriesDicts = []
	for seriesId in seriesIds:
		workDicts, seriesDict = getSeriesInfo(seriesId)
		allWorkDicts.extend(workDicts)
		seriesDicts.append(seriesDict)
	insertWorkRows(allWorkDicts)
	insertSeriesRows(seriesDicts)

def makeSequelsShelf(name, count):
	bookIds = getAllBooksFromShelf(name, count)
	bookToWorkIds = getBooksToWorks(bookIds)
	print "bookToWorkIds: ", bookToWorkIds
	workIds = set(bookToWorkIds.values())

	newBooks = set(bookIds).difference(bookToWorkIds.keys())
	print "new books: ", newBooks
	newBooks.update(getPossibleNewSeries(workIds))
	print "new books: ", newBooks
	workIds.update(processNewBooks(newBooks))

	unpublished, readInSeries = getReadInformation(workIds)
	print "readInSeries: "
	print readInSeries

	seriesToQuery = getSeriesToQuery(readInSeries.keys())
	print "series to query: ", seriesToQuery
	processSeries(seriesToQuery)

	booksToAdd = getBooksToAdd(readInSeries)
	print "books to add: ", booksToAdd

	return booksToAdd


	# # create new shelf
	# newShelfName = name + '-sequels'
	# print "creating new shelf"
	# goodreads.post('/user_shelves.xml', data = {
	# 	'user_shelf[name]': newShelfName
	# })
	# print "done creating new shelf: ", newShelfName

	# print "adding books to new shelf"
	# # add all books to new shelf
	# goodreads.post('/shelf/add_books_to_shelves.xml', data = {
	# 	'bookids': joinInts(booksToAdd),
	# 	'shelves': newShelfName + ",to-read"
	# })
	# print "done"

##############
# Flask Routes

@app.route('/')
@app.route("/index")
def index():
	if session.get('goodreads_token', False):
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

	session['goodreads_user_id'] = userId
	session['goodreads_user_name'] = username

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
	booksToAdd = makeSequelsShelf(request.json['name'], request.json['count'])

	shelfName = request.json['name']
	newShelfName = shelfName + ' Sequels'
	# print "getting books on shelf: ", request.json['name']
	# # get name of every book on shelf
	# getAllBooksFromShelf(request.json['name'], request.json['count'])

	booksToAdd = {k:v for k,v in booksToAdd.iteritems() if len(v) > 1}
	readBooks = {k:v[0] for k,v in booksToAdd.iteritems()}
	booksToAdd = {k:v[1:] for k,v in booksToAdd.iteritems()}
	seriesNames = getSeriesNames(booksToAdd.keys())

	# Get human readable information
	print "newShelfName: ", newShelfName

	print "rendering template"
	return render_template(
		'newshelf.html',
		booksToAdd=booksToAdd,
		readBooks=readBooks,
		seriesNames=seriesNames,
		newShelfName=newShelfName)

@app.route('/createShelf', methods=['POST'])
def createShelf():

	# # create new shelf
	# newShelfName = name + '-sequels'
	# print "creating new shelf"
	# goodreads.post('/user_shelves.xml', data = {
	# 	'user_shelf[name]': newShelfName
	# })
	# print "done creating new shelf: ", newShelfName

	# print "adding books to new shelf"
	# # add all books to new shelf
	# goodreads.post('/shelf/add_books_to_shelves.xml', data = {
	# 	'bookids': joinInts(booksToAdd),
	# 	'shelves': newShelfName + ",to-read"
	# })
	# print "done"

	return render_template('index.html')


@app.route('/denied')
def denied():
	return render_template('index.html', message="Maybe next time o/")

@app.route('/login')
def login():
	return goodreads.authorize(callback=url_for('oauth_authorized',
		next=request.args.get('next') or request.referrer or None))

@app.route('/resetdatabase')
def resetDatabase():
	init_db()

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