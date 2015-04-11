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

# Index landing page

import fw
import database

fw.write_header()
fw.render_header("Home - League Analyzer", ["navbar.css", "home.css", "fontello.css"])

fw.render("components/navbar", {
	"championsActiveClass": "",
	"itemsActiveClass": ""
})
fw.render("views/home")

fw.render_footer(["navbar.js"])
