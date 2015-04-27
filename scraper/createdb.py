# createdb package as part of scraper
# creates the tables for the database

import sys

from riotwatcher import RiotWatcher

def drop_db(c):
	# print("DROP THE (data)BASE!")
	c.execute("DROP TABLE IF EXISTS Champion")
	c.execute("DROP TABLE IF EXISTS Item")
	c.execute("DROP TABLE IF EXISTS Spell")
	# c.execute("DROP TABLE IF EXISTS Match")
	# c.execute("DROP TABLE IF EXISTS Ban")
	# c.execute("DROP TABLE IF EXISTS MatchSummoner")
	# c.execute("DROP TABLE IF EXISTS MatchSummonerItem")
	# print("WUWBWUWBUWBUWBUWBUBUW")

def fill_champions(c, api_key):
	api = RiotWatcher(api_key)
	try:
		all_champions = api.static_get_champion_list(None, None, None, None, "image")
	except:
		print("Error getting all champions:", sys.exc_info()[0])
		return

	for _, champion in all_champions["data"].iteritems():
		wiki_url = "http://leagueoflegends.wikia.com/wiki/" + champion["name"]

		splash_image = champion["key"] + "_0.jpg"

		c.execute('''
			INSERT INTO Champion (Id, Name, Title, WikiLink, Image, SplashImage)
			VALUES (?, ?, ?, ?, ?, ?)
		''', (champion["id"], champion["name"], champion["title"],
			wiki_url, champion["image"]["full"], splash_image))

def fill_items(c, api_key):
	api = RiotWatcher(api_key)
	try:
		all_items = api.static_get_item_list(None, None, None, "image")
	except:
		print("Error getting all items:", sys.exc_info()[0])
		return

	for _, item in all_items["data"].iteritems():
		wiki_url = "http://leagueoflegends.wikia.com/wiki/" + item["name"]

		c.execute('''
			INSERT INTO Item (Id, Name, Description, WikiLink, Image)
			VALUES (?, ?, ?, ?, ?)
		''', (item["id"], item["name"], item["description"],
			wiki_url, item["image"]["full"]))

def fill_spells(c, api_key):
	api = RiotWatcher(api_key)
	try:
		all_spells = api.static_get_summoner_spell_list(None, None, None, None, "image")
	except:
		print("Error getting all spells:", sys.exc_info()[0])
		return

	for _, spell in all_spells["data"].iteritems():
		c.execute('''
			INSERT INTO Spell (Id, Name, Image)
			VALUES (?, ?, ?)
		''', (spell["id"], spell["name"], spell["image"]["full"]))

def fill_db(c, api_key):
	fill_champions(c, api_key)
	fill_items(c, api_key)
	fill_spells(c, api_key)


def create_db(c, api_key, drop=False):
	if drop:
		drop_db(c)

	c.execute('''
		CREATE TABLE IF NOT EXISTS MatchSummoner(
			Id INTEGER PRIMARY KEY,
			InternalMatchId INTEGER NOT NULL REFERENCES Match(Id),
			Tier VARCHAR(15) NOT NULL,
			ChampionId INTEGER NOT NULL REFERENCES Champion(Id),
			DidWin BOOLEAN NOT NULL,
			IsOnBlue BOOLEAN NOT NULL,
			Kills INTEGER NOT NULL,
			Deaths INTEGER NOT NULL,
			Assists INTEGER NOT NULL,
			NormalWards INTEGER NOT NULL,
			VisionWards INTEGER NOT NULL,
			Minions INTEGER NOT NULL,
			PhysicalDealt INTEGER NOT NULL,
			MagicDealt INTEGER NOT NULL,
			TrueDealt INTEGER NOT NULL,
			PhysicalDealtChampions INTEGER NOT NULL,
			MagicDealtChampions INTEGER NOT NULL,
			TrueDealtChampions INTEGER NOT NULL,
			PhysicalReceived INTEGER NOT NULL,
			MagicReceived INTEGER NOT NULL,
			TrueReceived INTEGER NOT NULL,
			Lane TEXT NOT NULL,
			Role TEXT NOT NULL,
			AllyJungleMonsters INTEGER NOT NULL,
			EnemyJungleMonsters INTEGER NOT NULL,
			Gold INTEGER NOT NULL,
			SpellA INTEGER NOT NULL REFERENCES Spell(Id),
			SpellB INTEGER NOT NULL REFERENCES Spell(Id),
			DoubleKills INTEGER NOT NULL,
			TripleKills INTEGER NOT NULL,
			QuadraKills INTEGER NOT NULL,
			PentaKills INTEGER NOT NULL
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS Champion(
			Id INTEGER PRIMARY KEY,
			Name TEXT NOT NULL,
			Title TEXT NOT NULL,
			WikiLink TEXT NOT NULL,
			Image TEXT NOT NULL,
			SplashImage TEXT NOT NULL
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS Ban(
			Id INTEGER PRIMARY KEY,
			InternalMatchId INTEGER NOT NULL REFERENCES Match(Id),
			ChampionId INTEGER NOT NULL REFERENCES Champion(Id)
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS Item(
			Id INTEGER PRIMARY KEY,
			Name TEXT NOT NULL,
			Description TEXT,
			WikiLink TEXT NOT NULL,
			Image TEXT NOT NULL
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS Spell(
			Id INTEGER PRIMARY KEY,
			Name TEXT NOT NULL,
			Image TEXT NOT NULL
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS Match(
			Id INTEGER PRIMARY KEY,
			MatchId INTEGER NOT NULL,
			Region VARCHAR(5) NOT NULL,
			WinnerIsBlue BOOLEAN NOT NULL,
			AverageTier VARCHAR(15) NOT NULL,
			Time TIMESTAMP NOT NULL,
			QueueType TEXT NOT NULL,
			LengthSeconds INTEGER NOT NULL
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS MatchSummonerItem(
			Id INTEGER PRIMARY KEY,
			MatchSummonerId INTEGER NOT NULL REFERENCES MatchSummoner(Id),
			ItemId INTEGER NOT NULL REFERENCES Item(Id)
		)
	''')

	if drop:
		fill_db(c, api_key)
