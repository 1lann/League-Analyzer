# coding=UTF-8

# Framework pacakge
# Wrapper for templates package

import sys
import templates
from templates import webRootPath
from string import Template

endpointVersion = "5.8.1"

def write_header():
	print("Content-type: text/html; charset=utf-8\r")

def redirect(path):
	print("Status: 302 Found")
	print("Location: " + webRootPath + path + "\r\n\r\n")
	sys.exit()

def render_header(title, stylesheets = None):
	args = {}
	args["title"] = title
	args["unsafe_stylesheets"] = ""

	if stylesheets != None:
		for css in stylesheets:
			args["unsafe_stylesheets"] += '<link rel="stylesheet" type="text/css" href="' + webRootPath + '/static/css/' + css + '">\n'

	templates.execute_by_name("htmlHeader", args)

def render_footer(scripts = None):
	args = {}
	args["unsafe_scripts"] = ""

	if scripts != None:
		for script in scripts:
			args["unsafe_scripts"] += '<script type="text/javascript" src="' + webRootPath + '/static/js/' + script + '"></script>\n'

	templates.execute_by_name("htmlFooter", args)

def render(template, args = None):
	templates.execute_by_name(template, args)

def template(templateContent, args):
	templates.execute(Template(templateContent), args)
