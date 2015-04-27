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
champion_id = formValues.getvalue("id")

database.open_db()

champion_info = database.get_champion_info(champion_id)
if not champion_info:
	champion_id = "102"
	champion_info = database.get_champion_info(champion_id)
	# fw.redirect("/controllers/champions/landing.py")

fw.write_header()
fw.render_header(champion_info["championName"] + " - League Analyzer",
["navbar.css", "champion-statistic.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "active",
	"itemsActiveClass": ""
})

row_template = Template('''<tr onclick="location.assign('$webRootPath/controllers/champions/general.py?filter=$filter');">
	<td class="heading">$statistic</td>
	<td class="value">$value</td>
	<td class="rank">$rank</td>
	<td class="deviation">$deviation</td>
</tr>''')

render_args = {}

# Headings and static information

render_args["champion_name"] = champion_info["championName"]
render_args["champion_splash"] = champion_info["championSplash"]
render_args["champion_title"] = champion_info["championTitle"]

# Statistics table

def twoFormat(num):
	return ("%.2f" % num) + "%"

def oneFormat(num):
	return ("%.1f" % num)

def thousandFormat(num):
	return "{:,}".format(int(num))

def timeFormat(num):
	return ("%.1f" % (num / 60)) + " mins"

statistics_set = [
	{
		"function": database.get_most_popular_champions,
		"heading": "Pick rate",
		"key": "percentage",
		"format": twoFormat,
		"link": "mostpopular",
		"invert": False
	},
	{
		"function": database.get_most_wins_champions,
		"heading": "Winrate",
		"key": "percentage",
		"format": twoFormat,
		"link": "mostwins",
		"invert": False
	},
	{
		"function": database.get_most_banned_champions,
		"heading": "Ban rate",
		"key": "percentage",
		"format": twoFormat,
		"link": "mostbanned",
		"invert": False
	},
	{
		"function": database.get_longest_game_length_champions,
		"heading": "Game length",
		"key": "num",
		"format": timeFormat,
		"link": "longestlength",
		"invert": None
	},
	{
		"function": database.get_most_kills_champions,
		"heading": "Kills",
		"key": "num",
		"format": oneFormat,
		"link": "mostkills",
		"invert": False
	},
	{
		"function": database.get_most_assists_champions,
		"heading": "Assists",
		"key": "num",
		"format": oneFormat,
		"link": "mostassists",
		"invert": False
	},
	{
		"function": database.get_most_kills_champions,
		"heading": "Deaths",
		"key": "num",
		"format": oneFormat,
		"link": "mostkills",
		"invert": True
	},
	{
		"function": database.get_most_damage_dealt_champions,
		"heading": "Damage dealt",
		"key": "num",
		"format": thousandFormat,
		"link": "mostdamagedealt",
		"invert": False
	},
	{
		"function": database.get_most_damage_received_champions,
		"heading": "Damage received",
		"key": "num",
		"format": thousandFormat,
		"link": "mostdamagereceived",
		"invert": False
	},
	{
		"function": database.get_most_gold_champions,
		"heading": "Gold earned",
		"key": "num",
		"format": thousandFormat,
		"link": "mostgold",
		"invert": False
	}
]

render_args["unsafe_statistics"] = ""
plays = 0

for stat in statistics_set:
	results = stat["function"]()
	resultsSum = 0
	rank = ""
	rawValue = 0
	for i in range(len(results)):
		result = results[i]
		resultsSum += result[stat["key"]]
		if result["championId"] == int(champion_id):
			rank = str(i + 1)
			if stat["link"] == "mostpopular":
				plays = result["plays"]
			rawValue = result[stat["key"]]

	average = resultsSum / len(results)

	row_args = {}

	rawDeviaton = float(rawValue) / float(average)
	if rawDeviaton >= 1:
		rawDeviaton -= 1
		deviation = "+" + twoFormat(rawDeviaton * 100)
	else:
		rawDeviaton = 1 - rawDeviaton
		deviation = "-" + twoFormat(rawDeviaton * 100)

	if stat["invert"] == True:
		if rawValue > average:
			row_args["deviation"] = '<span class="deviation-bad">' + deviation + '</span>'
		else:
			row_args["deviation"] = '<span class="deviation-good">' + deviation + '</span>'
	elif stat["invert"] == False:
		if rawValue > average:
			row_args["deviation"] = '<span class="deviation-good">' + deviation + '</span>'
		else:
			row_args["deviation"] = '<span class="deviation-bad">' + deviation + '</span>'
	else:
		row_args["deviation"] = deviation

	row_args["statistic"] = stat["heading"]
	row_args["value"] = stat["format"](rawValue)
	row_args["rank"] = '<span style="font-weight:bold;">' + str(rank) + "</span>/" + str(len(results))
	row_args["webRootPath"] = fw.webRootPath
	row_args["filter"] = stat["link"]

	render_args["unsafe_statistics"] += row_template.safe_substitute(row_args)

# Damage composition

composition = database.get_damage_dealt_composition(champion_id)

render_args["magic_dealt"] = twoFormat(composition["percent_magic"] * 100)
render_args["physical_dealt"] = twoFormat(composition["percent_physical"] * 100)
render_args["true_dealt"] = twoFormat(composition["percent_true"] * 100)

# Item tables

popular_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage"></td>
	<td>$itemName</td>
	<td>$percentage%</td>
	<td>$winrate%</td>
</tr>
''')

most_popular = database.get_most_popular_items(champion_id)

top_items = []

for i in range(30):
	top_items.append(most_popular[i]["itemId"])

item_winrates = database.get_champion_items_wins(champion_id, top_items)

most_popular_rows = ""
for i in range(30):
	args = copy.copy(most_popular[i])

	for item in item_winrates:
		if item["itemId"] == args["itemId"]:
			raw_percent = float(args["percentage"]) / 100.0
			total_games = int(raw_percent * float(plays))
			args["winrate"] = ("%.2f" % ((float(item["wins"]) / total_games) * 100.0))
			break

	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % args["percentage"])
	args["webRootPath"] = fw.webRootPath
	most_popular_rows += popular_row_template.safe_substitute(args)

render_args["unsafe_most_popular"] = most_popular_rows

# most_wins = database.get_most_wins_items(champion_id)
# most_wins_rows = ""
# for i in range(30):
# 	args = copy.copy(most_wins[i])
# 	args["rank"] = str(i + 1)
# 	args["endpointVersion"] = fw.endpointVersion
# 	args["percentage"] = ("%.2f" % ((float(args["wins"])/float(args["total"])) * 100.0))
# 	args["wins"] = str(args["wins"])
# 	args["webRootPath"] = fw.webRootPath
# 	most_wins_rows += wins_row_template.safe_substitute(args)

# render_args["unsafe_most_wins"] = most_wins_rows



fw.render("views/champions/champion", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
