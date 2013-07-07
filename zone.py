import sqlite3, re, hashlib
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

# our main views
@app.route('/')
def index():
	return render_template('index.html')

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
