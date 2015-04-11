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
from string import Template

database.open_db()

fw.write_header()
fw.render_header("Items - League Analyzer", ["navbar.css", "items-landing.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})

popularRowTemplate = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$percentage%</td>
</tr>
''')

winsRowTemplate = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$wins</td>
	<td>$percentage%</td>
</tr>
''')

renderArgs = {}

highestWins = database.get_highest_wins_items()
highestWinsRows = ""
for i in range(10):
	args = copy.copy(highestWins[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0))
	args["wins"] = str(args["wins"])
	args["webRootPath"] = fw.webRootPath
	highestWinsRows += winsRowTemplate.safe_substitute(args)

renderArgs["unsafe_highestWins"] = highestWinsRows


lowestWins = database.get_lowest_wins_items()
lowestWinsRows = ""
for i in range(10):
	args = copy.copy(lowestWins[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0 ))
	args["wins"] = str(args["wins"])
	args["webRootPath"] = fw.webRootPath
	lowestWinsRows += winsRowTemplate.safe_substitute(args)

renderArgs["unsafe_lowestWins"] = lowestWinsRows


mostPopular = database.get_most_popular_items()
mostPopularRows = ""
for i in range(10):
	args = copy.copy(mostPopular[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	temp = ("%.2f" % args["percentage"])
	args["percentage"] = temp
	args["webRootPath"] = fw.webRootPath
	mostPopularRows += popularRowTemplate.safe_substitute(args)

renderArgs["unsafe_mostPopular"] = mostPopularRows


leastPopular = database.get_least_popular_items()
leastPopularRows = ""
for i in range(10):
	args = copy.copy(leastPopular[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	temp = ("%.2f" % args["percentage"])
	args["percentage"] = temp
	args["webRootPath"] = fw.webRootPath
	leastPopularRows += popularRowTemplate.safe_substitute(args)

renderArgs["unsafe_leastPopular"] = leastPopularRows


fw.render("views/items/landing", renderArgs)

fw.render_footer(["navbar.js"])

database.close_db()
