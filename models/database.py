# Get root path

import os

rootPath = os.path.dirname(os.path.abspath(__file__))
while os.path.basename(rootPath) != "analyzer":
	rootPath = os.path.dirname(rootPath)

# Database package for reading

import sqlite3
import json
from string import Template

conn = None
c = None

def open_db():
	global conn
	global c
	conn = sqlite3.connect(rootPath + "/analyzer.db")
	c = conn.cursor()
	c.execute('''
		CREATE TABLE IF NOT EXISTS Cache(
			Id INTEGER PRIMARY KEY,
			Key TEXT NOT NULL,
			Value TEXT NOT NULL
		)
	''')
	c.execute("pragma synchronous = off")
	conn.commit()

def clear_cache():
	c.execute("DROP TABLE IF EXISTS Cache")
	conn.commit()

def close_db():
	conn.commit()
	c.close()
	conn.close()

def get_cache(key):
	c.execute("SELECT Value FROM Cache WHERE Key = ?", (json.dumps(key),))
	result = c.fetchone()
	if result == None:
		return None
	else:
		return json.loads(result[0])

def store_cache(key, value):
	c.execute("INSERT INTO Cache (Key, Value) VALUES (?, ?)", (json.dumps(key), json.dumps(value),))
	conn.commit()

def get_most_wins_items(champion=None):
	global c

	cache_key = {"action": "get_most_winrate_items", "champion": champion}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	# TODO Add champion id checking

	championStatementA = ""
	championStatementB = ""
	if champion != None:
		championStatementA = "AND ms.ChampionId = " + str(champion)
		championStatementB = "AND mstotal.ChampionId = " + str(champion)

	query = Template('''
	SELECT Item.Id, Item.Name, Item.Description, Item.Image, COUNT(*) as wins, (
		SELECT COUNT(*)
		FROM MatchSummonerItem msitotal
		INNER JOIN MatchSummoner mstotal
		WHERE msitotal.ItemId = Item.Id
		AND msitotal.MatchSummonerId = mstotal.Id
		$championStatementB
	) as total
	FROM Item
	INNER JOIN MatchSummonerItem msi
	INNER JOIN MatchSummoner ms
	WHERE msi.ItemId = Item.Id
	AND msi.MatchSummonerId = ms.Id
	$championStatementA
	AND ms.DidWin = 1
	GROUP BY Item.Id
	ORDER BY (CAST(wins AS float)/CAST(total AS float)) DESC
	''').safe_substitute(
		{"championStatementA": championStatementA,
		"championStatementB": championStatementB}
	)

	c.execute(query)
	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["itemId"] = result[0]
		parsedResult["itemName"] = result[1]
		parsedResult["itemDescription"] = result[2]
		parsedResult["itemImage"] = result[3]
		parsedResult["wins"] = result[4]
		parsedResult["total"] = result[5]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults


def get_champion_items_wins(champion, items):
	global c

	cache_key = {"action": "get_item_winrate", "champion": champion, "items": items}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	parsedResults = []

	for item in items:
		c.execute('''
		SELECT Item.Id, Item.Name, Item.Description, Item.Image, COUNT(*) as wins
		FROM Item
		INNER JOIN MatchSummonerItem msi
		INNER JOIN MatchSummoner ms
		WHERE Item.Id = ?
		AND msi.ItemId = Item.Id
		AND msi.MatchSummonerId = ms.Id
		AND ms.ChampionId = ?
		AND ms.DidWin = 1
		ORDER BY wins DESC
		''', (item, champion))

		result = c.fetchone()

		parsedResult = {}
		parsedResult["itemId"] = result[0]
		parsedResult["itemName"] = result[1]
		parsedResult["itemDescription"] = result[2]
		parsedResult["itemImage"] = result[3]
		parsedResult["wins"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)

	return parsedResults

def get_least_wins_items(champion=None):
	results = get_most_wins_items(champion)
	results.reverse()
	return results

def get_most_popular_items(champion=None):
	global c

	cache_key = {"action": "get_most_popular_items", "champion": champion}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	# TODO Add champion id checking

	championStatementA = ""
	championStatementB = ""
	if champion != None:
		championStatementA = "AND ms.ChampionId = " + str(champion)
		championStatementB = "WHERE mstotal.ChampionId = " + str(champion)

	query = Template('''
	SELECT Item.Id, Item.Name, Item.Description, Item.Image,
	COUNT(*), (CAST(COUNT(*) AS float) / (
		SELECT CAST(COUNT(*) AS float)
		FROM MatchSummoner mstotal
		$championStatementB
	)) * 100.0 as buyrate
	FROM Item
	INNER JOIN MatchSummonerItem msi
	INNER JOIN MatchSummoner ms
	WHERE msi.ItemId = Item.Id
	AND msi.MatchSummonerId = ms.Id
	$championStatementA
	GROUP BY Item.Id
	ORDER BY buyrate DESC
	''').safe_substitute(
		{"championStatementA": championStatementA,
		"championStatementB": championStatementB}
	)

	c.execute(query)
	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["itemId"] = result[0]
		parsedResult["itemName"] = result[1]
		parsedResult["itemDescription"] = result[2]
		parsedResult["itemImage"] = result[3]
		parsedResult["purchases"] = result[4]
		parsedResult["percentage"] = result[5]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_least_popular_items(champion=None):
	results = get_most_popular_items(champion)
	results.reverse()
	return results

def get_most_popular_champions(item=None):
	global c

	cache_key = {"action": "get_most_popular_champions", "item": item}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	if item == None:
		c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, COUNT(*),
		(CAST(COUNT(*) AS float) / (
			SELECT CAST(COUNT(distinct InternalMatchId) AS float) FROM MatchSummoner
		)) * 100.0 as pickrate
		FROM MatchSummoner
		INNER JOIN Champion
		WHERE Champion.Id = MatchSummoner.ChampionId
		GROUP BY Champion.Id
		ORDER BY pickrate DESC
		''')
	else:
		c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, COUNT(*),
		(CAST(COUNT(*) AS float) / (
			SELECT CAST(COUNT(*) AS float)
			FROM MatchSummoner totalms
			WHERE totalms.ChampionId = Champion.Id
		)) * 100.0 as pickrate
		FROM MatchSummoner ms
		INNER JOIN Champion
		INNER JOIN MatchSummonerItem msi
		WHERE Champion.Id = ms.ChampionId
		AND msi.ItemId = ?
		AND msi.MatchSummonerId = ms.Id
		GROUP BY Champion.Id
		ORDER BY pickrate DESC
		''', (item,))

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["plays"] = result[4]
		parsedResult["percentage"] = result[5]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_least_popular_champions(item=None):
	results = get_most_popular_champions(item)
	results.reverse()
	return results

def get_most_banned_champions():
	global c

	cache_key = {"action": "get_most_banned_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
	SELECT Champion.Id, Champion.Name, Champion.Title,
	Champion.Image, COUNT(*),
	(CAST(COUNT(*) AS float) / (
		SELECT CAST(COUNT(distinct totalban.InternalMatchId) AS float) FROM Ban totalban
	)) * 100.0 as banrate
	FROM Ban
	INNER JOIN Champion
	WHERE Champion.Id = Ban.ChampionId
	GROUP BY Champion.Id
	ORDER BY banrate DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["plays"] = result[4]
		parsedResult["percentage"] = result[5]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_most_wins_champions():
	global c

	cache_key = {"action": "get_most_winrate_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
	SELECT Champion.Id, Champion.Name, Champion.Title,
	Champion.Image, COUNT(*),
	(CAST(COUNT(*) AS float) / (
		SELECT CAST(COUNT(*) AS float) FROM MatchSummoner totalms
		WHERE totalms.ChampionId = Champion.Id
	)) * 100.0 as winrate
	FROM MatchSummoner ms
	INNER JOIN Champion
	WHERE Champion.Id = ms.ChampionId
	AND ms.DidWin = 1
	GROUP BY Champion.Id
	ORDER BY winrate DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["plays"] = result[4]
		parsedResult["percentage"] = result[5]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_least_wins_champions():
	results = get_most_wins_champions()
	results.reverse()
	return results

def get_most_deaths_champions():
	global c

	cache_key = {"action": "get_most_deaths_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, AVG(ms.Deaths) as avgDeaths
		FROM MatchSummoner ms
		INNER JOIN Champion
		WHERE Champion.Id = ms.ChampionId
		GROUP BY Champion.Id
		ORDER BY avgDeaths DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_most_kills_champions():
	global c

	cache_key = {"action": "get_most_kills_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, AVG(ms.Kills) as avgKills
		FROM MatchSummoner ms
		INNER JOIN Champion
		WHERE Champion.Id = ms.ChampionId
		GROUP BY Champion.Id
		ORDER BY avgKills DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_most_assists_champions():
	global c

	cache_key = {"action": "get_most_assists_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, AVG(ms.Assists) as avgAssists
		FROM MatchSummoner ms
		INNER JOIN Champion
		WHERE Champion.Id = ms.ChampionId
		GROUP BY Champion.Id
		ORDER BY avgAssists DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_longest_game_length_champions():
	global c

	cache_key = {"action": "get_longest_game_length"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached


	c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, AVG(Match.LengthSeconds) as length
		FROM MatchSummoner ms
		INNER JOIN Champion
		INNER JOIN Match
		WHERE Champion.Id = ms.ChampionId
		AND ms.InternalMatchId = Match.Id
		GROUP BY Champion.Id
		ORDER BY length DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_shortest_game_length_champions():
	results = get_longest_game_length_champions()
	results.reverse()
	return results

def get_most_damage_dealt_champions(damageType=None):
	# can be "true", "magic" or "physical"

	damageTypes = {
		"magic": "MagicDealtChampions",
		"physical": "PhysicalDealtChampions",
		"true": "TrueDealtChampions"
	}

	global c

	cache_key = {"action": "get_most_damage_dealt_champions", "damageType": damageType}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	if damageType == None:
		c.execute('''
			SELECT Champion.Id, Champion.Name, Champion.Title,
			Champion.Image,
			AVG(ms.PhysicalDealtChampions + ms.MagicDealtChampions
				+ ms.TrueDealtChampions) as totalDamage
			FROM MatchSummoner ms
			INNER JOIN Champion
			WHERE Champion.Id = ms.ChampionId
			GROUP BY Champion.Id
			ORDER BY totalDamage DESC
		''')
	else:
		c.execute(('''
			SELECT Champion.Id, Champion.Name, Champion.Title,
			Champion.Image, AVG(ms.%s) as damage
			FROM MatchSummoner ms
			INNER JOIN Champion
			WHERE Champion.Id = ms.ChampionId
			GROUP BY Champion.Id
			ORDER BY damage DESC
		''' % damageTypes[damageType]))

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults


def get_most_damage_received_champions():
	global c

	cache_key = {"action": "get_most_damage_received_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image,
		AVG(ms.PhysicalReceived + ms.MagicReceived
			+ ms.TrueReceived) as totalDamage
		FROM MatchSummoner ms
		INNER JOIN Champion
		WHERE Champion.Id = ms.ChampionId
		GROUP BY Champion.Id
		ORDER BY totalDamage DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults

def get_most_gold_champions():
	global c

	cache_key = {"action": "get_most_gold_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT Champion.Id, Champion.Name, Champion.Title,
		Champion.Image, AVG(ms.Gold) as gold
		FROM MatchSummoner ms
		INNER JOIN Champion
		WHERE Champion.Id = ms.ChampionId
		GROUP BY Champion.Id
		ORDER BY gold DESC
	''')

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResult["num"] = result[4]
		parsedResults.append(parsedResult)

	store_cache(cache_key, parsedResults)
	return parsedResults


def get_average_game_length():
	global c

	cache_key = {"action": "get_average_game_length"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(LengthSeconds)
		FROM Match
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result


def get_average_kills():
	global c

	cache_key = {"action": "get_average_kills"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(Kills)
		FROM MatchSummoner
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result


def get_average_deaths():
	global c

	cache_key = {"action": "get_average_deaths"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(Deaths)
		FROM MatchSummoner
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result


def get_average_assists():
	global c

	cache_key = {"action": "get_average_assists"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(Assists)
		FROM MatchSummoner
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result


def get_average_damage_dealt_champions():
	global c

	cache_key = {"action": "get_average_damage_dealt_champions"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(PhysicalDealtChampions + MagicDealtChampions + TrueDealtChampions)
		FROM MatchSummoner
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result


def get_average_damage_received():
	global c

	cache_key = {"action": "get_average_damage_received"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(PhysicalReceived + MagicReceived + TrueReceived)
		FROM MatchSummoner
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result


def get_average_gold():
	global c

	cache_key = {"action": "get_average_gold"}

	cached = get_cache(cache_key)
	if cached != None:
		return cached

	c.execute('''
		SELECT AVG(Gold)
		FROM MatchSummoner
	''')

	result = c.fetchone()[0]

	store_cache(cache_key, result)

	return result

def get_champion_info(champion):
	global c

	c.execute('''
		SELECT Id, Name, Title, WikiLink, Image, SplashImage
		FROM Champion
		WHERE Id = ?
	''', (champion,))

	result = c.fetchone()

	if not result:
		return False

	parsedResult = {}
	parsedResult["championId"] = result[0]
	parsedResult["championName"] = result[1]
	parsedResult["championTitle"] = result[2]
	parsedResult["championWikiLink"] = result[3]
	parsedResult["championImage"] = result[4]
	parsedResult["championSplash"] = result[5]

	return parsedResult

def get_item_info(item):
	global c

	c.execute('''
		SELECT Id, Name, Description, Image
		FROM Item
		WHERE Id = ?
	''', (item,))

	result = c.fetchone()

	if not result:
		return False

	parsedResult = {}
	parsedResult["itemId"] = result[0]
	parsedResult["itemName"] = result[1]
	parsedResult["itemDescription"] = result[2]
	parsedResult["itemImage"] = result[3]

	return parsedResult

def get_damage_dealt_composition(champion):
	global c

	c.execute('''
		SELECT SUM(PhysicalDealtChampions),
		SUM(MagicDealtChampions),
		SUM(TrueDealtChampions)
		FROM MatchSummoner
		WHERE ChampionId = ?
	''', (champion,))

	result =  c.fetchone()

	physical_dealt = result[0]
	magic_dealt = result[1]
	true_dealt = result[2]

	total_dealt = float(physical_dealt + magic_dealt + true_dealt)

	result = {}
	result["percent_physical"] = float(physical_dealt) / total_dealt
	result["percent_magic"] = float(magic_dealt) / total_dealt
	result["percent_true"] = float(true_dealt) / total_dealt

	return result

def search_champions(query):
	global c

	c.execute('''
		SELECT Id, Name, Title, Image
		FROM Champion
		WHERE Name LIKE ?
	''', (query + "%",))

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["championId"] = result[0]
		parsedResult["championName"] = result[1]
		parsedResult["championTitle"] = result[2]
		parsedResult["championImage"] = result[3]
		parsedResults.append(parsedResult)

	return parsedResults

def search_items(query):
	global c

	c.execute('''
		SELECT Id, Name, Image
		FROM Item
		WHERE Name LIKE ?
	''', (query + "%",))

	results = c.fetchall()

	parsedResults = []
	for result in results:
		parsedResult = {}
		parsedResult["itemId"] = result[0]
		parsedResult["itemName"] = result[1]
		parsedResult["itemImage"] = result[2]
		parsedResults.append(parsedResult)

	return parsedResults
