from __future__ import with_statement
from flask import Flask, render_template, request, session, g, redirect, url_for, \
	 abort, flash
from flask.ext.classy import FlaskView, route
import requests, json, math

class db(FlaskView):
	def index(self):
		cur = g.db.execute(' SELECT gameid FROM exits GROUP BY gameid ORDER BY id LIMIT 100')
		bigdata = [row[0] for row in cur.fetchall()]
		return render_template('dbindex.html', games=bigdata)

	def post(self):
		return "Thanks for searching!"

		# pass or carry, exit with posession
		# chip, FP, FC, or other (x) without posession
			# but still successful
		# unsuccessful: Icing, pass turn over, carry turnover, turnover
	@route('/<int:gameid>/')	
	def view(self, gameid):
		# if you're logged in get your stats
		cur = g.db.execute("SELECT * FROM exits WHERE gameid = ? AND (team = '1' OR team = 'H') ORDER BY player", [gameid])
		allData = cur.fetchall()
		error = None
		if allData == []:
			error = "Home Team does not have data."
		mydata = {}
		total = 0
		default = [0]*8
		# load user names
		oGameID = str(gameid)[0:4]+"0"+str(gameid)[-5:]
		url = 'http://sareon.pythonanywhere.com/toi/roster/'+oGameID
		players = json.loads(requests.get(url).text)

		# calculate stats
		for d in allData:
			total += 1
			playerNum = d[7]
			exittype = d[6]
			if playerNum not in mydata:
				mydata[playerNum] = list(default)
				if str(playerNum) not in players['h']:
					mydata[playerNum][0] = '<Invalid PNum>'
				else:
					mydata[playerNum][0] = players['h'][str(playerNum)]
			mydata[playerNum][1] += 1
			if exittype in ['P', 'C']:
				mydata[playerNum][4] += 1
			if exittype in ['P', 'C', 'CH', 'FC', 'FP', 'X']:
				mydata[playerNum][3] += 1
			if exittype in ['I', 'T', 'CT', 'PT']:
				mydata[playerNum][2] += 1	
		# dictionary to list
		data = []
		for i in mydata:
			myrow = [i]+mydata[i]
			myrow[6] = float(myrow[5]) / myrow[2]	
			myrow[6] = math.ceil(myrow[6] * 1000.0) / 1000.0
			myrow[8] = float(myrow[4]) / myrow[2]	
			myrow[8] = math.ceil(myrow[8] * 1000.0) / 1000.0
			myrow[7] = '-'
			data.append(myrow)		

		# away team
		cur = g.db.execute("SELECT * FROM exits WHERE gameid = ? AND (team = '2' OR team = 'A') ORDER BY player", [gameid])
		allData = cur.fetchall()
		error2 = None
		if allData == []:
			error2 = "Away Team does not have data."
		mydata = {}
		total = 0
		default = [0]*7
		# calculate stats
		for d in allData:
			total += 1
			playerNum = d[7]
			exittype = d[6]
			if playerNum not in mydata:
				mydata[playerNum] = list(default)
				if str(playerNum) not in players['v']:
					mydata[playerNum][0] = '<Invalid PNum>'
				else:
					mydata[playerNum][0] = players['v'][str(playerNum)]
			mydata[playerNum][1] += 1
			if exittype in ['P', 'C']:
				mydata[playerNum][4] += 1
			if exittype in ['P', 'C', 'CH', 'FC', 'FP', 'X']:
				mydata[playerNum][3] += 1
			if exittype in ['I', 'T', 'CT', 'PT']:
				mydata[playerNum][2] += 1	
		# dictionary to list
		data2 = []
		for i in mydata:
			myrow = [i]+mydata[i]
			myrow[6] = float(myrow[5]) / myrow[2]	
			myrow[6] = math.ceil(myrow[6] * 1000.0) / 1000.0
			myrow[8] = float(myrow[4]) / myrow[2]	
			myrow[8] = math.ceil(myrow[8] * 1000.0) / 1000.0
			myrow[7] = '-'
			data2.append(myrow)	
		return render_template('dbview.html', data=data, error=error,
								error2=error2, data2=data2)