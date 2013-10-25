from __future__ import with_statement
from flask import Flask, render_template, request, session, g, redirect, url_for, \
	 abort, flash
from flask.ext.classy import FlaskView, route

import helpers

class admin(FlaskView):
	@helpers.admin_only
	# need to make this private
	def getAllGames(self):
		cur = g.db.execute('SELECT gameid FROM exits GROUP BY gameid ORDER BY gameid DESC')
		return [[str(x[0])[0:8]+" "+str(x[0])[8:], int(x[0])] for x in cur.fetchall()]

	@helpers.admin_only
	def index(self):
		return render_template('admin-home.html')

	@route('/fixrosternames')
	@helpers.admin_only
	def fixrosternames(self):
		games = self.getAllGames()
		return render_template('admin-fixrosternames.html', data=games)

	@route('/deletegame')
	@helpers.admin_only
	def deletegame(self):
		games = self.getAllGames()
		return render_template('admin-deletegame.html', data=games)

	@route('/deletegame/<int:gameid>')
	@helpers.admin_only
	def deletedata(self, gameid):
		cur = g.db.execute('DELETE FROM exits WHERE gameid=?', [gameid,])
		g.db.commit()
		return redirect(url_for('admin:deletegame'))

