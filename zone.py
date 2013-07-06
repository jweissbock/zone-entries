import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
from contextlib import closing

# configuration info
DATABASE = 'zone.db'
DEBUG = True
SECRET_KEY = 'I DONT KNOW WHAT IM DOING'
USERNAME = 'admin'
password = 'default'

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

# run the app
if __name__ == '__main__':
	app.run()
