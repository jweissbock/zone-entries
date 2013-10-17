from __future__ import with_statement
from flask import Flask, render_template, request, session, g, redirect, url_for, \
	 abort, flash
from flask.ext.classy import FlaskView, route
import requests, json, math

class db(FlaskView):
	def index(self):
		cur = g.db.execute(' SELECT gameid FROM exits GROUP BY gameid ORDER BY gameid DESC LIMIT 100')
		bigdata = [row[0] for row in cur.fetchall()]
		return render_template('dbindex.html', games=bigdata)

	def post(self):
		return "Thanks for searching!"

		# pass or carry, exit with posession
		# chip, FP, FC, or other (x) without posession
			# but still successful
		# unsuccessful: Icing, pass turn over, carry turnover, turnover
	# if we are logged in we want to get that users stats
	@route('/<int:gameid>/')	
	def view(self, gameid):
		# load user names
		oGameID = str(gameid)[0:4]+"0"+str(gameid)[-5:]
		url = 'http://sareon.pythonanywhere.com/toi/roster/'+oGameID
		# try-catch it, if it is not json
		try:
			players = json.loads(requests.get(url).text)
		except:
			players = {'h' : '', 'v' : ''}

		# data to be pre-loaded once
		default = [0]*8
		error, error2 = None, None
		data, data2 = [], []
		
		# loop through the chances
		for location in ['H', 'A']:
			mydata = {}
			total = 0
			teamNum = 2
			teamCode = 'A'
			teamPCode = 'v'
			tempError = None
			tempData = []

			# are we doing home or away stats?
			if location == 'H':
				teamNum = 1
				teamCode = 'H'	
				teamPCode = 'h'

			cur = g.db.execute("SELECT * FROM exits WHERE gameid = ? AND (team = ? OR team = ?) ORDER BY player", [gameid, teamNum, teamCode])
			allData = cur.fetchall()
			if allData == []:
				tempError = "Team does not have data."


			# calculate stats
			for d in allData:
				total += 1
				playerNum = d[7]
				exittype = d[6]
				if playerNum not in mydata:
					mydata[playerNum] = list(default)
					if str(playerNum) not in players[teamPCode]:
						mydata[playerNum][0] = '<Invalid Plr#>'
					else:
						mydata[playerNum][0] = players[teamPCode][str(playerNum)]
				mydata[playerNum][1] += 1
				if exittype in ['P', 'C']:
					mydata[playerNum][4] += 1
				if exittype in ['P', 'C', 'CH', 'FC', 'FP', 'X']:
					mydata[playerNum][3] += 1
				if exittype in ['I', 'T', 'CT', 'PT']:
					mydata[playerNum][2] += 1	

			# dictionary to list
			for i in mydata:
				myrow = [i]+mydata[i]
				myrow[6] = float(myrow[5]) / myrow[2]	
				myrow[6] = math.ceil(myrow[6] * 1000.0) / 1000.0
				myrow[8] = float(myrow[4]) / myrow[2]	
				myrow[8] = math.ceil(myrow[8] * 1000.0) / 1000.0
				myrow[7] = '-'
				tempData.append(myrow)		

			# assign the variables now
			if location == 'H':
				error = tempError
				data = tempData
			else:
				error2 = tempError
				data2 = tempData

		return render_template('dbview.html', data=data, error=error,
								error2=error2, data2=data2)