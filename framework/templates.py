# coding=UTF-8

webRootPath = "http://localhost/analyzer"

# Root path loader
import os
import sys

rootPath = os.path.dirname(os.path.abspath(__file__))
while os.path.basename(rootPath) != "analyzer":
	rootPath = os.path.dirname(rootPath)

# Templates pacakge


from string import Template
import cgi

templates = {}

templates["htmlHeader"] = Template("""
<!DOCTYPE html>
<html>
<head>
<title>$title</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="UTF-8">
<link href='//fonts.googleapis.com/css?family=Raleway:400,300,600' rel='stylesheet' type='text/css'>
<link rel="stylesheet" type="text/css" href="$webRootPath/static/css/skeleton.min.css">
<link rel="stylesheet" type="text/css" href="$webRootPath/static/css/common.css">
<script type="text/javascript" src="$webRootPath/static/js/jquery-2.1.3.min.js"></script>
$unsafe_stylesheets
</head>
<body>
""")

templates["htmlFooter"] = Template("""
<div class="footer">
	<div class="container">
		<p>Made by Jason Chu.</p>
		<p class="disclaimer">
			League Analyzer isn't endorsed by Riot Games and doesn't reflect
			the views or opinions of Riot Games or anyone officially involved
			in producing or managing League of Legends. League of Legends and
			Riot Games are trademarks or registered trademarks of Riot Games,
			Inc. League of Legends © Riot Games, Inc.
		</p>
	</div>
</div>
$unsafe_scripts
</body>
</html>
""")

def read_file(path):
	with open(path, 'r') as content_file:
		return content_file.read()

def execute(template, args):
	safeArgs = {"webRootPath": webRootPath}
	if args != None:
		for key, value in args.iteritems():
			if len(key) > 7 and key[:7] == "unsafe_":
				safeArgs[key] = value
			else:
				safeArgs[key] = cgi.escape(value)

	print(template.safe_substitute(safeArgs))

def execute_by_name(template_name, args = None):
	if template_name in templates:
		execute(templates[template_name], args)
	else:
		execute(Template(read_file(rootPath + "/" + template_name + ".html")), args)
