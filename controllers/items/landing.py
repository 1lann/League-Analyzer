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

fw.write_header()
fw.render_header("Items - League Analyzer", ["navbar.css", "items-landing.css", "fontello.css"])

fw.render("components/navbar", {
	"webRootPath": fw.webRootPath,
	"championsActiveClass": "",
	"itemsActiveClass": "active"
})


fw.render("views/items-landing")

fw.render_footer(["navbar.js"])
