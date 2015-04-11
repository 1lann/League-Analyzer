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
fw.render_header("Champions - League Analyzer", ["navbar.css", "champions-landing.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "active",
	"itemsActiveClass": ""
})

mostPopular = database.get_most_popular_champions()

highestWinrate = database.get_most_popular_champions()

mostBanned = database.get_most_popular_champions()

leastPopular = database.get_most_popular_champions()

lowestWinrate = database.get_most_popular_champions()

leastBanned = database.get_most_popular_champions()

fw.render("views/champions/landing")

fw.render_footer(["navbar.js"])

database.close_db()
