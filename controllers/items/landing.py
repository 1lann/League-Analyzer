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
fw.render_header("Items - League Analyzer", ["navbar.css", "landing.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})

popular_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$percentage%</td>
</tr>
''')

wins_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$wins</td>
	<td>$percentage%</td>
</tr>
''')

render_args = {}

most_wins = database.get_most_wins_items()
most_win_rows = ""
for i in range(10):
	args = copy.copy(most_wins[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0))
	args["wins"] = str(args["wins"])
	args["webRootPath"] = fw.webRootPath
	most_win_rows += wins_row_template.safe_substitute(args)

render_args["unsafe_mostWins"] = most_win_rows


least_wins = database.get_least_wins_items()
least_win_rows = ""
for i in range(10):
	args = copy.copy(least_wins[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0 ))
	args["wins"] = str(args["wins"])
	args["webRootPath"] = fw.webRootPath
	least_win_rows += wins_row_template.safe_substitute(args)

render_args["unsafe_leastWins"] = least_win_rows


most_popular = database.get_most_popular_items()
most_popular_rows = ""
for i in range(10):
	args = copy.copy(most_popular[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	temp = ("%.2f" % args["percentage"])
	args["percentage"] = temp
	args["webRootPath"] = fw.webRootPath
	most_popular_rows += popular_row_template.safe_substitute(args)

render_args["unsafe_mostPopular"] = most_popular_rows


least_popular = database.get_least_popular_items()
least_popular_rows = ""
for i in range(10):
	args = copy.copy(least_popular[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	temp = ("%.2f" % args["percentage"])
	args["percentage"] = temp
	args["webRootPath"] = fw.webRootPath
	least_popular_rows += popular_row_template.safe_substitute(args)

render_args["unsafe_leastPopular"] = least_popular_rows


fw.render("views/items/landing", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
