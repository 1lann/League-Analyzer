#!/usr/bin/python
# coding=UTF-8

import fw
import database

fw.write_header()
fw.render_header("Home", ["navbar.css", "home.css", "fontello.css"])

fw.render("components/navbar")
fw.render("views/home")

fw.render_footer()
