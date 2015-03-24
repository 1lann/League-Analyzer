#!/usr/bin/python

from string import Template
import cgi

templates = {}

templates["htmlHeader"] = Template("""
<html>
<head>
<title>$title</title>
<meta name=viewport content="width=device-width, initial-scale=1">
<link href='//fonts.googleapis.com/css?family=Raleway:400,300,600' rel='stylesheet' type='text/css'>
<link rel="stylesheet" type="text/css" href="css/skeleton.min.css">
$unsafe_stylesheets
</head>
<body>
""")

templates["htmlFooter"] = Template("""
$unsafe_scripts
</body>
</html>
""")

def readFile(path):
	with open(path, 'r') as content_file:
		return content_file.read()

def execute(template, args):
	safeArgs = {}
	if args != None:
		for key, value in args.iteritems():
			if len(key) > 7 and key[:7] == "unsafe_":
				safeArgs[key] = value
			else:
				safeArgs[key] = cgi.escape(value)

	print(template.safe_substitute(safeArgs))

def executeByName(templateName, args = None):
	if templateName in templates:
		execute(templates[templateName], args)
	else:
		execute(Template(readFile(templateName + ".html")), args)
