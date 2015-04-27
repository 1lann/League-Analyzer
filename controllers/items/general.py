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

# Items general page

import fw
import database
import copy
import cgi
from string import Template

formValues = cgi.FieldStorage()
filter = formValues.getvalue("filter")

popular_table_head = "<tr><th>Rank</th><th></th><th>Item</th><th>Buy Rate</th></tr>"

popular_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$percentage%</td>
</tr>
''')

wins_table_head = "<tr><th>Rank</th><th></th><th>Item</th><th>Wins</th><th>Winrate</th></tr>"

wins_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$wins</td>
	<td>$percentage%</td>
</tr>
''')

if filter == None or (filter != "mostwins" and filter != "leastwins" and
filter != "mostpopular" and filter != "leastpopular"):
	fw.redirect("/controllers/items/landing.py")

fw.write_header()
fw.render_header("Items Statistics - League Analyzer",
	["navbar.css", "landing.css", "fontello.css", "general.css"])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})

database.open_db()

render_args = {}

if filter == "mostwins":
	highest_wins = database.get_highest_wins_items()
	highest_wins_rows = ""
	for i in range(len(highest_wins)):
		args = copy.copy(highest_wins[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0))
		args["wins"] = str(args["wins"])
		args["webRootPath"] = fw.webRootPath
		highest_wins_rows += wins_row_template.safe_substitute(args)
	render_args["unsafe_tableHead"] = wins_table_head
	render_args["unsafe_table"] = highest_wins_rows
	render_args["tableTitle"] = "Items with the greatest winrates"

elif filter == "leastwins":
	least_wins = database.get_least_wins_items()
	least_wins_rows = ""
	for i in range(len(least_wins)):
		args = copy.copy(least_wins[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0 ))
		args["wins"] = str(args["wins"])
		args["webRootPath"] = fw.webRootPath
		least_wins_rows += wins_row_template.safe_substitute(args)
	render_args["unsafe_tableHead"] = wins_table_head
	render_args["unsafe_table"] = least_wins_rows
	render_args["tableTitle"] = "Items with the lowest winrates"

elif filter == "mostpopular":
	most_popular = database.get_most_popular_items()
	most_popular_rows = ""
	for i in range(len(most_popular)):
		args = copy.copy(most_popular[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		temp = ("%.2f" % args["percentage"])
		args["percentage"] = temp
		args["webRootPath"] = fw.webRootPath
		most_popular_rows += popular_row_template.safe_substitute(args)
	render_args["unsafe_tableHead"] = popular_table_head
	render_args["unsafe_table"] = most_popular_rows
	render_args["tableTitle"] = "Items which are bought the most"

elif filter == "leastpopular":
	least_popular = database.get_least_popular_items()
	least_popular_rows = ""
	for i in range(len(least_popular)):
		args = copy.copy(least_popular[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		temp = ("%.2f" % args["percentage"])
		args["percentage"] = temp
		args["webRootPath"] = fw.webRootPath
		least_popular_rows += popular_row_template.safe_substitute(args)
	render_args["unsafe_tableHead"] = popular_table_head
	render_args["unsafe_table"] = least_popular_rows
	render_args["tableTitle"] = "Items which are bought the least"


fw.render("views/items/general", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
