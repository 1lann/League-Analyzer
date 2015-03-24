#!/usr/bin/python

import cgi
import templates
from string import Template

def writeHeader():
	print("Content-type: text/html; charset=utf-8\r\n\r\n")

def renderHeader(title, stylesheets = None):
	args = {}
	args["title"] = title
	args["unsafe_stylesheets"] = ""

	if stylesheets != None:
		for css in stylesheets:
			args["unsafe_stylesheets"] += '<link rel="stylesheet" type="text/css" href="css/' + css + '">\n'

	templates.executeByName("htmlHeader", args)

def renderFooter(scripts = None):
	args = {}
	args["unsafe_scripts"] = ""

	if scripts != None:
		for script in scripts:
			args["unsafe_scripts"] += '<script type="text/javascript" src="js/' + script + '"></script>\n'

	templates.executeByName("htmlFooter", args)

def render(template, args = None):
	templates.executeByName(template, args)

def template(templateContent, args):
	templates.execute(Template(templateContent), args)
