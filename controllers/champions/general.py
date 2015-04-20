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
import cgi
from string import Template

formValues = cgi.FieldStorage()
filter = formValues.getvalue("filter")

picks_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Pick Rate</th></tr>"
wins_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Winrate</th></tr>"
bans_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Ban Rate</th></tr>"
kills_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Kills</th></tr>"
deaths_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Deaths</th></tr>"
assists_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Assists</th></tr>"
length_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Game Length</th></tr>"
damage_dealt_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Damage Dealt</th></tr>"
damage_received_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Damage Received</th></tr>"
gold_table_head = "<tr><th>Rank</th><th></th><th>Champion</th><th>Average Gold Earned</th></tr>"

row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/champions/champion.py?id=$championId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/champion/$championImage"></td>
	<td>$championName</td>
	<td>$percentage%</td>
</tr>
''')

game_length_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/champions/champion.py?id=$championId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/champion/$championImage"></td>
	<td>$championName</td>
	<td>$length mins</td>
</tr>
''')

num_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/champions/champion.py?id=$championId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/champion/$championImage"></td>
	<td>$championName</td>
	<td>$num</td>
</tr>
''')

znum_row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/champions/champion.py?id=$championId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/champion/$championImage"></td>
	<td>$championName</td>
	<td>$num</td>
</tr>
''')


if filter == None or (filter != "mostwins" and filter != "leastwins" and
filter != "mostpopular" and filter != "leastpopular" and
filter != "mostbanned" and filter != "leastbanned" and
filter != "shortestlength" and filter != "longestlength" and
filter != "mostkills" and filter != "mostdeaths" and
filter != "mostassists" and filter != "mostdamagedealt" and
filter != "mostdamagereceived" and filter != "mostgold"):
	fw.redirect("/controllers/champions/landing.py")


fw.write_header()
fw.render_header("Champions Statistics - League Analyzer",
["navbar.css", "landing.css", "fontello.css", "general.css"])

fw.render("components/navbar", {
	"championsActiveClass": "active",
	"itemsActiveClass": ""
})

database.open_db()

render_args = {}
selected_array = {}
selected_template = row_template
render_args["unsafe_table"] = ""

if filter == "mostwins":
	selected_array = database.get_most_wins_champions()
	render_args["unsafe_tableHead"] = wins_table_head
	render_args["tableTitle"] = "Champions with the greatest winrates"
elif filter == "leastwins":
	selected_array = database.get_least_wins_champions()
	render_args["unsafe_tableHead"] = wins_table_head
	render_args["tableTitle"] = "Champions with the lowest winrates"
elif filter == "mostpopular":
	selected_array = database.get_most_popular_champions()
	render_args["unsafe_tableHead"] = picks_table_head
	render_args["tableTitle"] = "Champions which are picked the most"
elif filter == "leastpopular":
	selected_array = database.get_least_popular_champions()
	render_args["unsafe_tableHead"] = picks_table_head
	render_args["tableTitle"] = "Champions which are picked the least"
elif filter == "mostbanned":
	selected_array = database.get_most_banned_champions()
	render_args["unsafe_tableHead"] = bans_table_head
	render_args["tableTitle"] = "Champions which are banned the most"
elif filter == "leastbanned":
	selected_array = database.get_least_banned_champions()
	render_args["unsafe_tableHead"] = bans_table_head
	render_args["tableTitle"] = "Champions which are banned the least"
elif filter == "longestlength":
	selected_array = database.get_longest_game_length_champions()
	selected_template = game_length_row_template
	render_args["unsafe_tableHead"] = length_table_head
	render_args["tableTitle"] = "Champions who have the longest average games"
elif filter == "shortestlength":
	selected_array = database.get_longest_game_length_champions()
	selected_template = game_length_row_template
	render_args["unsafe_tableHead"] = length_table_head
	render_args["tableTitle"] = "Champions who have the shortest average games"
elif filter == "mostkills":
	selected_array = database.get_most_kills_champions()
	selected_template = num_row_template
	render_args["unsafe_tableHead"] = kills_table_head
	render_args["tableTitle"] = "Champions who have the most kills per game"
elif filter == "mostdeaths":
	selected_array = database.get_most_deaths_champions()
	selected_template = num_row_template
	render_args["unsafe_tableHead"] = deaths_table_head
	render_args["tableTitle"] = "Champions who have the most deaths per game"
elif filter == "mostassists":
	selected_array = database.get_most_assists_champions()
	selected_template = num_row_template
	render_args["unsafe_tableHead"] = assists_table_head
	render_args["tableTitle"] = "Champions who have the most asssits per game"
elif filter == "mostdamagedealt":
	selected_array = database.get_most_damage_dealt_champions()
	selected_template = znum_row_template
	render_args["unsafe_tableHead"] = damage_dealt_table_head
	render_args["tableTitle"] = "Champions who deal the most damage to champions per game"
elif filter == "mostdamagereceived":
	selected_array = database.get_most_damage_received_champions()
	selected_template = znum_row_template
	render_args["unsafe_tableHead"] = damage_received_table_head
	render_args["tableTitle"] = "Champions who receive the most damage per game"
elif filter == "mostgold":
	selected_array = database.get_most_gold_champions()
	selected_template = znum_row_template
	render_args["unsafe_tableHead"] = gold_table_head
	render_args["tableTitle"] = "Champions who earn the most gold per game"

if selected_template == row_template:
	for i in range(len(selected_array)):
		args = copy.copy(selected_array[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["percentage"] = ("%.2f" % args["percentage"])
		args["webRootPath"] = fw.webRootPath
		render_args["unsafe_table"] += selected_template.safe_substitute(args)
elif selected_template == game_length_row_template:
	for i in range(len(selected_array)):
		args = copy.copy(selected_array[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["length"] = ("%.1f" % args["num"] / 60)
		args["webRootPath"] = fw.webRootPath
		render_args["unsafe_table"] += selected_template.safe_substitute(args)
elif selected_template == num_row_template:
	for i in range(len(selected_array)):
		args = copy.copy(selected_array[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["num"] = ("%.1f" % args["num"])
		args["webRootPath"] = fw.webRootPath
		render_args["unsafe_table"] += selected_template.safe_substitute(args)
elif selected_template == znum_row_template:
	for i in range(len(selected_array)):
		args = copy.copy(selected_array[i])
		args["rank"] = str(i + 1)
		args["endpointVersion"] = fw.endpointVersion
		args["num"] = ("%.0f" % args["num"])
		args["webRootPath"] = fw.webRootPath
		render_args["unsafe_table"] += selected_template.safe_substitute(args)


fw.render("views/champions/general", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
