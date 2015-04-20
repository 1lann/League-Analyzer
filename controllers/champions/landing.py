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
fw.render_header("Champions - League Analyzer", ["navbar.css", "landing.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "active",
	"itemsActiveClass": ""
})

row_template = Template('''
<tr onclick="location.assign('$webRootPath/controllers/champions/champion.py?id=$championId');">
	<td>$rank</td>
	<td><img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/champion/$championImage"></td>
	<td>$championName</td>
	<td>$percentage%</td>
</tr>
''')

length_row_template = Template('''
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

render_args = {}

# Sorry for the boilerplate code!
# I would refactor it but I'm too lazy.

most_popular = database.get_most_popular_champions()
most_popular_rows = ""
for i in range(10):
	args = copy.copy(most_popular[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % args["percentage"])
	args["webRootPath"] = fw.webRootPath
	most_popular_rows += row_template.safe_substitute(args)

render_args["unsafe_mostPopular"] = most_popular_rows

most_winrate = database.get_most_wins_champions()
most_winrate_rows = ""
for i in range(10):
	args = copy.copy(most_winrate[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % args["percentage"])
	args["webRootPath"] = fw.webRootPath
	most_winrate_rows += row_template.safe_substitute(args)

render_args["unsafe_mostWins"] = most_winrate_rows

most_banned = database.get_most_banned_champions()
most_banned_rows = ""
for i in range(10):
	args = copy.copy(most_banned[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % args["percentage"])
	args["webRootPath"] = fw.webRootPath
	most_banned_rows += row_template.safe_substitute(args)

render_args["unsafe_mostBanned"] = most_banned_rows

least_popular = database.get_least_popular_champions()
least_popular_rows = ""
for i in range(10):
	args = copy.copy(least_popular[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % args["percentage"])
	args["webRootPath"] = fw.webRootPath
	least_popular_rows += row_template.safe_substitute(args)

render_args["unsafe_leastPopular"] = least_popular_rows

least_winrate = database.get_least_wins_champions()
least_winrate_rows = ""
for i in range(10):
	args = copy.copy(least_winrate[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["percentage"] = ("%.2f" % args["percentage"])
	args["webRootPath"] = fw.webRootPath
	least_winrate_rows += row_template.safe_substitute(args)

render_args["unsafe_leastWins"] = least_winrate_rows

longest_length = database.get_longest_game_length_champions()
longest_length_rows = ""
for i in range(10):
	args = copy.copy(longest_length[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["length"] = ("%.1f" % (args["num"] / 60))
	args["webRootPath"] = fw.webRootPath
	longest_length_rows += length_row_template.safe_substitute(args)

render_args["unsafe_longestLength"] = longest_length_rows

shortest_length = database.get_shortest_game_length_champions()
shortest_length_rows = ""
for i in range(10):
	args = copy.copy(shortest_length[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["length"] = ("%.1f" % (args["num"] / 60))
	args["webRootPath"] = fw.webRootPath
	shortest_length_rows += length_row_template.safe_substitute(args)

render_args["unsafe_shortestLength"] = shortest_length_rows

most_kills = database.get_most_kills_champions()
most_kills_rows = ""
for i in range(10):
	args = copy.copy(most_kills[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["num"] = ("%.1f" % args["num"])
	args["webRootPath"] = fw.webRootPath
	most_kills_rows += num_row_template.safe_substitute(args)

render_args["unsafe_mostKills"] = most_kills_rows

most_deaths = database.get_most_deaths_champions()
most_deaths_rows = ""
for i in range(10):
	args = copy.copy(most_deaths[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["num"] = ("%.1f" % args["num"])
	args["webRootPath"] = fw.webRootPath
	most_deaths_rows += num_row_template.safe_substitute(args)

render_args["unsafe_mostDeaths"] = most_deaths_rows

most_assists = database.get_most_assists_champions()
most_assists_rows = ""
for i in range(10):
	args = copy.copy(most_assists[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["num"] = ("%.1f" % args["num"])
	args["webRootPath"] = fw.webRootPath
	most_assists_rows += num_row_template.safe_substitute(args)

render_args["unsafe_mostAssists"] = most_assists_rows

most_gold = database.get_most_gold_champions()
most_gold_rows = ""
for i in range(10):
	args = copy.copy(most_gold[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["num"] = ("%.0f" % args["num"])
	args["webRootPath"] = fw.webRootPath
	most_gold_rows += num_row_template.safe_substitute(args)

render_args["unsafe_mostGold"] = most_gold_rows

most_damage = database.get_most_damage_dealt_champions()
most_damage_rows = ""
for i in range(10):
	args = copy.copy(most_damage[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["num"] = ("%.0f" % args["num"])
	args["webRootPath"] = fw.webRootPath
	most_damage_rows += num_row_template.safe_substitute(args)

render_args["unsafe_mostDamage"] = most_damage_rows

most_damage_received = database.get_most_damage_received_champions()
most_damage_received_rows = ""
for i in range(10):
	args = copy.copy(most_damage_received[i])
	args["rank"] = str(i + 1)
	args["endpointVersion"] = fw.endpointVersion
	args["num"] = ("%.0f" % args["num"])
	args["webRootPath"] = fw.webRootPath
	most_damage_received_rows += num_row_template.safe_substitute(args)

render_args["unsafe_mostDamageReceived"] = most_damage_received_rows


render_args["averagePickrate"] = "%.2f" % ()


render_args["averageBanrate"] = "%.2f" % ()


render_args["averageGameLength"] = "%.1f" % ()


render_args["averageKills"] = "%.1f" % ()


render_args["averageDeaths"] = "%.1f" % ()


render_args["averageAssists"] = "%.1f" % ()


render_args["averageDamage"] = "%.0f" % ()


render_args["averageDamageReceived"] = "%.0f" % ()


render_args["averageGold"] = "%.0f" % ()


fw.render("views/champions/landing", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
