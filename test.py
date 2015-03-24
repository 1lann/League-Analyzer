#!/usr/bin/python

import cgi
import fw
from string import Template

fw.writeHeader()
fw.renderHeader("Home", ["navbar.css", "home.css", "common.css", "fontello.css"])

fw.render("components/navbar")
fw.render("views/home")

fw.renderFooter()

