from functools import wraps
from flask import g, session, request, redirect, url_for

# get user id
# get users ID
def getUserId():
	cur = g.db.execute('SELECT id FROM users WHERE email=?', [session.get('logged_in')])
	fetchd = cur.fetchone()
	return fetchd[0]

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session.get('logged_in'):
			return redirect(url_for('login'))
		else: print getUserId()
		return f(*args, **kwargs)
	return decorated_function

def admin_only(f):
	@wraps(f)
	def admin_function(*args, **kwargs):
		cur = g.db.execute('SELECT admin FROM users WHERE email=?', [session.get('logged_in')])
		fetchd = cur.fetchone()
		if fetchd == None or fetchd[0] != 1: return redirect(url_for('login'))
		return f(*args, **kwargs)
	return admin_function
