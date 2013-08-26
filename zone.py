import sqlite3, re, hashlib, json, os
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
from contextlib import closing

# configuration info
DATABASE = 'zone.db'
DEBUG = True
SECRET_KEY = 'I DONT KNOW WHAT IM DOING'
USERNAME = 'admin'
PASSWORD = 'default'

# out application
app = Flask(__name__)
app.config.from_object(__name__)

# database stuff
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

# get user id
# get users ID
def getUserId():
	cur = g.db.execute('SELECT id FROM users WHERE email=?', [session.get('logged_in')])
	fetchd = cur.fetchone()
	return fetchd[0]

# our main views
def allowed_file(filename):
	ALLOWED_EXTENSIONS = set(['xls', 'xlsm', 'xlsx'])
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		file = request.files['file']
		data = request.form['data']
		year = request.form['year']
		gameid = request.form['gameid']
		team = request.form['team']
		if data not in ['1', '2']:
			message = "Not a valid entry type"
		elif year not in [str(x) for x in range(2013, 2014)]:
			message = "Not a valid year"
		elif len(gameid) not in [5,6] or not gameid.isdigit():
			message = "game id is not valid."
		elif int(gameid) < 20000 or int(gameid) >= 40000:
			message = "Game id is not in the valid range"
		elif team not in ['1', '2']:
			message = "Not a valid team"
		elif file and allowed_file(file.filename):
			from werkzeug import secure_filename
			filename = secure_filename(file.filename)
			UPLOAD_FOLDER = 'uploads/'
			fullpath = os.path.join(UPLOAD_FOLDER, filename)
			print fullpath
			file.save(fullpath)
			# parse it here
			os.remove(fullpath)
			message = "Successfully uploaded"
		else:
			message = "Not a valid excel file"
		flash(message)
		return redirect(url_for('index'))
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

# zone entries
@app.route('/addzen')
def addzen():
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('add-zen.html')

@app.route('/myze')
def myze():
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	# get users ID
	userid = getUserId()
	# get all users games
	cur = g.db.execute('SELECT gameid FROM exits WHERE tracker = ? GROUP BY gameid ORDER BY gameid DESC', [userid])
	bigdata = [list(row) for row in cur.fetchall()]
	#return render_template('allgames.html', alldata=bigdata)
	return render_template('my-ze.html', alldata=bigdata)

# main page for adding zone entries
@app.route('/addze')
@app.route('/addze/<int:gid>')	
def addze(gid=None):
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	# deal with editting
	# if gid not None, then load all data into an object and pass it
	bigdata = None
	if gid is not None:
		gidyear = str(gid)[:8]
		gameid = str(gid)[8:]
		cur = g.db.execute('SELECT * FROM exits WHERE tracker = ? and gameid = ? ORDER BY id', [getUserId(), gid])
		bigdata = [list(row) for row in cur.fetchall()]
	return render_template('add-ze.html', data=bigdata)

# save data
@app.route('/saveze', methods=['POST'])
def saveze():
	response = {}
	response['success'] = False
	response['message'] = None
	response['row'] = -1
	# check if logged in
	if not session.get('logged_in'):
		response['message'] = "Please login."
		return json.dumps(response)
	gameidyear = request.form['gameidyear']
	gameid = request.form['gameid']
	gid = gameidyear + gameid
	team = request.form['team']
	zentries = request.form['table']
	# check if gameidyear is 8 digit number
	if len(gameidyear) != 8 and not gameidyear.isdigit():
		response['message'] = "Game ID Year is not valid."
		return json.dumps(response)
	# check if gameid is a 5 digit number
	elif len(gameid) != 5 and not gameid.isdigit():
		response['message'] = "Game ID is not valid"
		return json.dumps(response)
	# check if team in H or A
	elif team not in ['H', 'A']:
		response['message'] = "Team is not valid"
		return json.dumps(response)

	# try and decode json
	zentries = json.loads(zentries)
	loop = 1

	# loop through
	for ze in zentries:
		response['row'] = loop
		# check if period in 1, 2, 3
		if ze['period'] not in ['1','2','3']:
			response['message'] = 'ZE %s does not have a valid period' % (loop)
			return json.dumps(response)
		# check if time is in dd:dd
		elif len(ze['time']) not in [4,5] or ':' not in ze['time']:
			response['message'] = 'ZE %s does not have a valid time' % (loop)
			return json.dumps(response)
		# check if exit 1 of 10
		elif ze['exit'] not in ['C', 'P', 'CH', 'I', 'FP', 'PT', 'FC', 'CT', 'T', 'X']: 
			response['message'] = 'ZE %s does not have a valid exit type' % (loop)
			return json.dumps(response)
		# check if player is d or OPP
		elif not ze['player'].isdigit() and ze['player'] != "OPP":
			response['message'] = 'ZE %s does not have a valid Player' % (loop)
			return json.dumps(response)
		# check if stength is dvd
		elif len(ze['strength']) != 3:
			response['message'] = 'ZE %s does not have a valid strength' % (loop)
			return json.dumps(response)
		# check if pressure Y or N
		elif ze['pressure'] not in ['Y', 'N']:
			response['message'] = 'ZE %s does not have a valid pressure' % (loop)
			return json.dumps(response)
		loop += 1
	# get user id from session
	cur = g.db.execute('SELECT id FROM users WHERE email=?', [session.get('logged_in')])
	fetchd = cur.fetchone()
	if fetchd is None:
		response['message'] = 'Something has gone wrong - you don\'t exist'
		return json.dumps(response)
	userid = fetchd[0]
	try:
		# delete all entries for this game for this user
		g.db.execute('DELETE FROM exits WHERE gameid = ? and tracker = ?', [gid, userid])
		g.db.commit()
		# loop through entries again
		for ze in zentries:
			# save each item
			g.db.execute('INSERT INTO exits (gameid, tracker, team, period, time, exittype, player, pressure, strength) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
							[gid, userid, team, ze['period'], ze['time'], ze['exit'], ze['player'], ze['pressure'], ze['strength']])
			g.db.commit()
	except:
		response['message'] = 'Something went wrong with saving on the server side.  Please contact Josh.'
		return json.dumps(response)
	# response
	response['success'] = True
	response['message'] = 'Successfully saved.'
	return json.dumps(response)

# sign up users
@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		# count rows
		cur = g.db.execute('SELECT * FROM users WHERE email=?', [request.form['email']])
		if not re.match(r'[^@]+@[^@]+\.[^@]+', request.form['email']):
			error = 'This is not a valid email.'
		elif cur.fetchone() is not None:
			error = 'This email is already in use.'
		elif len(request.form['password']) < 8:
			error = 'The password must be a minimum of 8 characters.'
		else:
			password = hashlib.sha224(request.form['password']).hexdigest()
			g.db.execute('INSERT INTO users (email, password) VALUES (?,?)',
				[request.form['email'], password])
			g.db.commit()
			session['logged_in'] = request.form['email']
			flash('You\'ve successfully registered!')
			return redirect(url_for('index'))
	return render_template('register.html', error=error)

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = password = hashlib.sha224(request.form['password']).hexdigest()
		cur = g.db.execute('SELECT * FROM users WHERE email=? AND password=?', [username, password])
		fetchd = cur.fetchone()
		if fetchd is None:
			error = 'Invalid login credentials.'
		else:
			session['logged_in'] = username
			flash('You were logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)

#logout
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('index'))

# run the app
if __name__ == '__main__':
	app.run()
