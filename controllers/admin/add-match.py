#!/usr/bin/python
# coding=UTF-8

# Models and framework loader
import os
import sys

rootPath = os.path.dirname(os.path.abspath(__file__))
while os.path.basename(rootPath) != "analyzer":
	rootPath = os.path.dirname(rootPath)

sys.path.append(rootPath + "/models")
sys.path.append(rootPath + "/framework")

# Index landing page

import fw
import cgi
import datetime
import database

formValues = cgi.FieldStorage()

if formValues.getvalue("add_data") == "true":
	errors = []

	try:
		time = datetime.datetime.fromtimestamp(int(formValues.getvalue("time")) / 1000)
	except:
		errors.append("Invalid UNIX time specified")

	try:
		match_id = int(formValues.getvalue("match_id"))
	except:
		errors.append("Invalid match ID (must be a number)")

	region = formValues.getvalue("region")
	if region == None:
		errors.append("A region must be specified")

	blue_win = formValues.getvalue("blue_win")
	if blue_win != "1" and blue_win != "0":
		errors.append("Whether blue team won must be a \"0\" or a \"1\"")

	tier = formValues.getvalue("tier")
	if tier == None:
		errors.append("The average tier must be specified")

	queue_type = formValues.getvalue("queue_type")
	if queue_type == None:
		errors.append("The queue type must be specified")

	length = formValues.getvalue("length")
	if length == None:
		errors.append("The length must be specified")

database.open_db()

fw.write_header()
fw.render_header("Add Match - League Analyzer", ["admin.css", "fontello.css"])

try:
	errors
except NameError:
	fw.render("views/admin/add-match", {"unsafe_alert": ""})
else:
	if len(errors) == 0:
		try:
			database.c.execute('''
				INSERT INTO Match (MatchId, Region, WinnerIsBlue,
					AverageTier, Time, QueueType, LengthSeconds)
				VALUES (?, ?, ?, ?, ?, ?, ?)
				''',
				(match_id, region, int(blue_win),
				tier, time, queue_type, length)
			)
			database.close_db()
			success = """
			<div class="success">
				<span class="success-heading">The match was successfully added</span>
			</div>
			"""
			fw.render("views/admin/add-match", {"unsafe_alert": success})
		except:
			alert = """
			<div class="error">
				<span class="error-heading">The following errors occured while verifying the data:</span>
				<ul>
				<li>Database execution error!</li>
				</ul>
			</div>
			"""
			fw.render("views/admin/add-match", {"unsafe_alert": alert})
	else:
		rows = ""

		for error in errors:
			rows += "<li>" + error + "</li>"


		alert = ("""
		<div class="error">
			<span class="error-heading">The following errors occured while verifying the data:</span>
			<ul>
			%s
			</ul>
		</div>
		""" % rows)

	fw.render("views/admin/add-match", {"unsafe_alert": alert})


fw.render_footer()
