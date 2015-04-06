# coding=UTF-8

# Framework pacakge
# Wrapper for templates package

import cgi
import templates
from string import Template

def write_header():
	print("Content-type: text/html; charset=utf-8\r")

def render_header(title, stylesheets = None):
	args = {}
	args["title"] = title
	args["unsafe_stylesheets"] = ""

	if stylesheets != None:
		for css in stylesheets:
			args["unsafe_stylesheets"] += '<link rel="stylesheet" type="text/css" href="static/css/' + css + '">\n'

	templates.execute_by_name("htmlHeader", args)

def render_footer(scripts = None):
	args = {}
	args["unsafe_scripts"] = ""

	if scripts != None:
		for script in scripts:
			args["unsafe_scripts"] += '<script type="text/javascript" src="static/js/' + script + '"></script>\n'

	templates.execute_by_name("htmlFooter", args)

def render(template, args = None):
	templates.execute_by_name(template, args)

def template(templateContent, args):
	templates.execute(Template(templateContent), args)
