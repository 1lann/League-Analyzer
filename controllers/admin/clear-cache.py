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

database.open_db()

fw.write_header()
fw.render_header("Clear Cache - Administration")

database.clear_cache()

database.close_db()

print('''
<div class="container">
<h2>League Analyzer Administration</h2>
<h4>Cache cleared</h4>
</div>
''')

fw.render_footer()
