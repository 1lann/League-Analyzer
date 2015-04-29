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
fw.render_header("Administration - League Analyzer", ["admin.css", "fontello.css"])

fw.render("views/admin/index")

fw.render_footer()
