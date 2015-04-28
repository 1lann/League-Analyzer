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

#  page

import fw
import database
import copy
import cgi
from string import Template

formValues = cgi.FieldStorage()
query = formValues.getvalue("query")

if query == None:
	query = ""

database.open_db()

results = database.search_items(query)

fw.write_header()
fw.render_header("Items Search - League Analyzer",
["navbar.css", "search.css", "fontello.css" ])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})

if query == "":
	fw.render("views/items/no-search")
else:
	render_args = {}

	render_args["query"] = query

	row_template = Template('''
		<tr onclick="location.assign('$webRootPath/controllers/items/item.py?id=$itemId');">
			<td class="result-image">
				<img src="http://ddragon.leagueoflegends.com/cdn/$endpointVersion/img/item/$itemImage">
			</td>
			<td class="result-name-item">$itemName</td>
		</tr>
	''')

	render_args["unsafe_results"] = ""
	render_args["unsafe_no_results"] = ""

	for result in results:
		row_args = copy.copy(result)
		row_args["endpointVersion"] = fw.endpointVersion
		row_args["webRootPath"] = fw.webRootPath
		render_args["unsafe_results"] += row_template.safe_substitute(row_args)

	if len(results) == 0:
		render_args["unsafe_no_results"] = "<h3>Your search query yielded no results!</h3>"

	fw.render("views/items/search", render_args)

fw.render_footer(["navbar.js"])

database.close_db()
