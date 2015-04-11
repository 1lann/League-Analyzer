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

# Items landing page

import fw
import database
import copy
import sys
import cgi
from string import Template

formValues = cgi.FieldStorage()
filter = formValues.getvalue("filter")

popularTableHead = "<tr><th>Rank</th><th></th><th>Item</th><th>Buy Rate</th></tr>"

popularRowTemplate = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$percentage%</td>
</tr>
''')

winsTableHead = "<tr><th>Rank</th><th></th><th>Item</th><th>Wins</th><th>Winrate</th></tr>"

winsRowTemplate = Template('''
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
	sys.exit()

fw.write_header()
fw.render_header("Items Statistics - League Analyzer", ["navbar.css", "items-landing.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})

database.open_db()

renderArgs = {}

if filter == "mostwins":
	highestWins = database.get_highest_wins_items()
	highestWinsRows = ""
	for i in range(len(highestWins)):
		args = copy.copy(highestWins[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0))
		args["wins"] = str(args["wins"])
		args["webRootPath"] = fw.webRootPath
		highestWinsRows += winsRowTemplate.safe_substitute(args)
	renderArgs["unsafe_tableHead"] = winsTableHead
	renderArgs["unsafe_table"] = highestWinsRows
	renderArgs["tableTitle"] = "Items with the greatest win rates"

elif filter == "leastwins":
	lowestWins = database.get_lowest_wins_items()
	lowestWinsRows = ""
	for i in range(len(lowestWins)):
		args = copy.copy(lowestWins[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0 ))
		args["wins"] = str(args["wins"])
		args["webRootPath"] = fw.webRootPath
		lowestWinsRows += winsRowTemplate.safe_substitute(args)
	renderArgs["unsafe_tableHead"] = winsTableHead
	renderArgs["unsafe_table"] = lowestWinsRows
	renderArgs["tableTitle"] = "Items with the lowest win rates"

elif filter == "mostpopular":
	mostPopular = database.get_most_popular_items()
	mostPopularRows = ""
	for i in range(len(mostPopular)):
		args = copy.copy(mostPopular[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		temp = ("%.2f" % args["percentage"])
		args["percentage"] = temp
		args["webRootPath"] = fw.webRootPath
		mostPopularRows += popularRowTemplate.safe_substitute(args)
	renderArgs["unsafe_tableHead"] = popularTableHead
	renderArgs["unsafe_table"] = mostPopularRows
	renderArgs["tableTitle"] = "Items which are bought the most"

elif filter == "leastpopular":
	leastPopular = database.get_least_popular_items()
	leastPopularRows = ""
	for i in range(len(leastPopular)):
		args = copy.copy(leastPopular[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		temp = ("%.2f" % args["percentage"])
		args["percentage"] = temp
		args["webRootPath"] = fw.webRootPath
		leastPopularRows += popularRowTemplate.safe_substitute(args)
	renderArgs["unsafe_tableHead"] = popularTableHead
	renderArgs["unsafe_table"] = leastPopularRows
	renderArgs["tableTitle"] = "Items which are bought the least"


fw.render("views/items/general", renderArgs)

fw.render_footer(["navbar.js"])

database.close_db()
