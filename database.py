# Database package for reading

import sqlite3

conn = None
c = None

def open_db():
	global conn
	global c
	conn = sqlite3.connect("league.db")
	c = conn.cursor()

def close_db():
	c.commit()
	conn.close()

