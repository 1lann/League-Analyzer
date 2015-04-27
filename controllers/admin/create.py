#!/usr/bin/python
# coding=UTF-8

# Models and framework loader
import os
import sys

rootPath = os.path.dirname(os.path.abspath(__file__))
while os.path.basename(rootPath) != "analyzer":
	rootPath = os.path.dirname(rootPath)

sys.path.append(rootPath + "/scraper")
sys.path.append(rootPath + "/framework")
sys.path.append(rootPath + "/models")

import createdb
import fw
import database

database.open_db()

api_key = "90063c6c-4471-455a-b58d-d6d32b0a040c"

fw.write_header()
fw.render_header("Create Database - Administration")

database.clear_cache()
createdb.create_db(database.c, api_key, True)

print('''
<div class="container">
<h2>League Analyzer Administration</h2>
<h4>Static database metadata refreshed</h4>
</div>
''')

database.close_db()

fw.render_footer()
