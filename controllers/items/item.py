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

# Champions statistic page

import fw
import copy
import database
import cgi
from string import Template

formValues = cgi.FieldStorage()
item_id = formValues.getvalue("id")

database.open_db()

item_info = database.get_item_info(item_id)
if not item_info:
	fw.redirect("/controllers/items/landing.py")

fw.write_header()
fw.render_header(item_info["itemName"] + " - League Analyzer",
["navbar.css", "item-statistic.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})

render_args = {}

# Headings and static information

render_args["webRootPath"] = fw.webRootPath
render_args["endpointVersion"] = fw.endpointVersion

render_args["item_name"] = item_info["itemName"]
render_args["item_image"] = item_info["itemImage"]
render_args["unsafe_item_description"] = item_info["itemDescription"]

popular_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/champions/champion.py?id=$championId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/champion/$championImage"></td>
	<td>$championName</td>
	<td>$percentage%</td>
</tr>
''')

most_popular_items = database.get_most_popular_items()

render_args["num_items"] = str(len(most_popular_items))

for i in range(len(most_popular_items)):
	if str(most_popular_items[i]["itemId"]) == item_id:
		render_args["buy_rank"] = str(i + 1)
		render_args["buy_rate"] = ("%.2f" % most_popular_items[i]["percentage"])
		break

most_wins_items = database.get_most_wins_items()
for i in range(len(most_wins_items)):
	if str(most_wins_items[i]["itemId"]) == item_id:
		render_args["wins_rank"] = str(i + 1)
		render_args["winrate"] = ("%.2f" % ((float(most_wins_items[i]["wins"]) / float(most_wins_items[i]["total"])) * 100))
		break

render_args["unsafe_most_popular"] = ""

most_popular_champions = database.get_most_popular_champions(item_id)

for i in range(min(30, len(most_popular_champions))):
	row_args = copy.copy(most_popular_champions[i])
	row_args["rank"] = str(i + 1)
	row_args["percentage"] = ("%.2f" % row_args["percentage"])
	row_args["endpointVersion"] = fw.endpointVersion
	row_args["webRootPath"] = fw.webRootPath
	render_args["unsafe_most_popular"] += popular_row_template.safe_substitute(row_args)


fw.render("views/items/item", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
