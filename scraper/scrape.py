# riot games API data scraping tool

from riotwatcher import RiotWatcher
from riotwatcher import RateLimit
from riotwatcher import EUROPE_WEST
from riotwatcher import OCEANIA
from riotwatcher import EUROPE_NORDIC_EAST
from riotwatcher import NORTH_AMERICA
from riotwatcher import KOREA
import seed

from createdb import create_db

import os
import sys
import sqlite3
import datetime
import time
import traceback

regions_apis = []

# pls no stealrino my production key
api_key = "90063c6c-4471-455a-b58d-d6d32b0a040c"
prod_limits = (RateLimit(40, 10), RateLimit(1000, 600), )

# 0
regions_apis.append(RiotWatcher(api_key, default_region=EUROPE_WEST, limits=prod_limits))
# 1
regions_apis.append(RiotWatcher(api_key, default_region=NORTH_AMERICA, limits=prod_limits))
# 2
regions_apis.append(RiotWatcher(api_key, default_region=OCEANIA, limits=prod_limits))
# 3
regions_apis.append(RiotWatcher(api_key, default_region=EUROPE_NORDIC_EAST, limits=prod_limits))
# 4
regions_apis.append(RiotWatcher(api_key, default_region=KOREA, limits=prod_limits))

db_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..") + "/analyzer.db"

print("Using database at: " + db_path)
conn = sqlite3.connect(db_path)
c = conn.cursor()

create_db(c, api_key)
conn.commit()

all_tiers = [
	"UNRANKED",
	"BRONZE",
	"SILVER",
	"GOLD",
	"PLATNIUM",
	"DIAMOND",
	"CHALLENGER"
]


def get_average_tier(tiers):
	global all_tiers
	total_tier = 0
	for player_tier in tiers:
		for tier_index in range(len(all_tiers)):
			if all_tiers[tier_index] == player_tier:
				total_tier += tier_index
				break

	average_tier_index = int(round(float(total_tier)/float(len(tiers))))
	return all_tiers[average_tier_index]

def store_player_item_data(c, player, match_data, internal_match_id, match_summoner_id):
	item_purchases = []
	player_id = player["participantId"]

	timeline = match_data["timeline"]["frames"]
	for frame in timeline:
		if "events" in frame:
			frame_events = frame["events"]
			for event in  frame_events:
				if event["eventType"] == "ITEM_PURCHASED" and event["participantId"] == player_id:
					if (not event["itemId"] in item_purchases):
						item_purchases.append(event["itemId"])

						try:
							c.execute('''
								INSERT INTO MatchSummonerItem (MatchSummonerId, ItemId)
								VALUES (?, ?)
								''',
								(match_summoner_id,
								event["itemId"])
							)
						except sqlite3.Error as e:
							print("SQLite store player item data error:", e.args[0])
							continue
						except:
							print("JSON store player item data error: ", sys.exc_info()[0])
							print(sys.exc_info()[1])
							continue



def store_player_data(c, player, match_data, internal_match_id):
	role = "unknown"

	if player["spell1Id"] == 11 or player["spell2Id"] == 11:
		role = "jungle"

	if player["timeline"]["lane"] == "BOTTOM" or player["timeline"]["lane"] == "BOT":
		role = "carry"
		for otherPlayer in match_data["participants"]:
			if (otherPlayer["timeline"]["lane"] == "BOTTOM" or otherPlayer["timeline"]["lane"] == "BOT") and (otherPlayer["participantId"] != player["participantId"]):
				if otherPlayer["stats"]["minionsKilled"] > player["stats"]["minionsKilled"]:
					role = "support"

	if player["timeline"]["lane"] == "JUNGLE" and role != "jungle":
		if player["spell1Id"] == 12 or player["spell1Id"] == 12:
			role = "top"
		else:
			role = "mid"
	elif player["timeline"]["lane"] == "MIDDLE":
		role = "mid"
	elif player["timeline"]["lane"] == "TOP":
		role = "top"

	stats = player["stats"]

	try:
		c.execute('''
			INSERT INTO MatchSummoner (InternalMatchId, Tier, ChampionId,
				DidWin, IsOnBlue, Kills, Deaths, Assists, NormalWards,
				VisionWards, Minions, PhysicalDealt, MagicDealt,
				TrueDealt, PhysicalDealtChampions, MagicDealtChampions,
				TrueDealtChampions, PhysicalReceived, MagicReceived,
				TrueReceived, Lane, Role, AllyJungleMonsters,
				EnemyJungleMonsters, Gold, SpellA, SpellB, DoubleKills,
				TripleKills, QuadraKills, Pentakills)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
				?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			''',
			(internal_match_id,
			player["highestAchievedSeasonTier"],
			player["championId"],
			stats["winner"],
			(player["teamId"] == 100),
			stats["kills"],
			stats["deaths"],
			stats["assists"],
			(stats["wardsPlaced"] - stats["visionWardsBoughtInGame"]),
			stats["visionWardsBoughtInGame"],
			stats["minionsKilled"],
			stats["physicalDamageDealt"],
			stats["magicDamageDealt"],
			stats["trueDamageDealt"],
			stats["physicalDamageDealtToChampions"],
			stats["magicDamageDealtToChampions"],
			stats["trueDamageDealtToChampions"],
			stats["physicalDamageTaken"],
			stats["magicDamageTaken"],
			stats["trueDamageTaken"],
			player["timeline"]["lane"],
			role,
			stats["neutralMinionsKilledTeamJungle"],
			stats["neutralMinionsKilledEnemyJungle"],
			stats["goldEarned"],
			player["spell1Id"],
			player["spell2Id"],
			stats["doubleKills"],
			stats["tripleKills"],
			stats["quadraKills"],
			stats["pentaKills"])
		)
	except sqlite3.Error as e:
		print("SQLite match summoner insert error:", e.args[0])
		return False
	except:
		print("JSON match summoner error: ", sys.exc_info()[0])
		print(sys.exc_info()[1])
		return False

	try:
		c.execute('''
			SELECT Id FROM MatchSummoner
			WHERE InternalMatchId = ? AND ChampionId = ? AND IsOnBlue = ?
			''',
			(internal_match_id, player["championId"], (player["teamId"] == 100))
		)
		match_summoner_id = c.fetchone()[0]
	except sqlite3.Error as e:
		print("SQLite match summoner get error:", e.args[0])
		return False
	except:
		print("JSON match summoner get error: ", sys.exc_info()[0])
		print(sys.exc_info()[1])
		return False

	return store_player_item_data(c, player, match_data, internal_match_id, match_summoner_id)

def store_match_data(c, match_data):
	tiers = []

	for player in match_data["participants"]:
		tiers += [player["highestAchievedSeasonTier"]]

	average_tier = get_average_tier(tiers)

	game_time = datetime.datetime.fromtimestamp(int(match_data["matchCreation"]/1000))

	if match_data["teams"][0]["winner"]:
		winner_is_blue = (match_data["teams"][0]["teamId"] == 100)
	else:
		winner_is_blue = (match_data["teams"][1]["teamId"] == 100)

	try:
		c.execute('''
			INSERT INTO Match (MatchId, Region, WinnerIsBlue,
				AverageTier, Time, QueueType, LengthSeconds)
			VALUES (?, ?, ?, ?, ?, ?, ?)
			''',
			(match_data["matchId"],
			api.default_region,
			winner_is_blue,
			average_tier, game_time,
			match_data["queueType"],
			match_data["matchDuration"])
		)
	except sqlite3.Error as e:
		print("SQLite match insert error:", e.args[0])
		return False
	except:
		print("JSON match error: ", sys.exc_info()[0])
		print(sys.exc_info()[1])
		return False

	try:
		c.execute("SELECT Id FROM Match WHERE MatchId = ? AND Region = ?",
			(match_data["matchId"], api.default_region))
		internal_match_id = c.fetchone()[0]
	except sqlite3.Error as e:
		print("SQLite select match error:", e.args[0])
		return False

	return internal_match_id

def store_ban_data(c, bans, internal_match_id):
	for ban in bans:
		try:
			c.execute('''
				INSERT INTO Ban (InternalMatchId, ChampionId)
				VALUES (?, ?)
				''',
				(internal_match_id,
				ban["championId"])
			)
		except sqlite3.Error as e:
			print("SQLite ban insert error:", e.args[0])
			return False
		except:
			print("JSON ban error: ", sys.exc_info()[0])
			print(sys.exc_info()[1])
			return False
	return True

last_now = datetime.datetime.fromtimestamp(0)

# Set process_queue or load seeds
for i in range(len(regions_apis)):
	regions_apis[i].process_queue = []
	# regions_apis[i].process_queue = seed.region(regions_apis[i].default_region)

while True:
	temp_now = datetime.datetime.utcnow()
	last_five_minutes = temp_now.minute - (temp_now.minute % 5)
	five_now = int(time.mktime(temp_now.replace(minute=last_five_minutes, second=0).timetuple()))

	# Get new batch of URF games
	if last_now != five_now:
		last_now = five_now
		for api in regions_apis:
			try:
				games = api.api_challenge(five_now)
			except:
				print("Error retrieving URF games for region " +
					api.default_region + " and time " + string(five_now))
				print(sys.exc_info()[0])
				print(sys.exc_info()[1])
				continue

			api.process_queue += games

	# Get data from queue
	for api in regions_apis:
		for game_id in api.process_queue:
			try:
				conn.commit()
				try:
					match_data = api.get_match(game_id, None, True)
				except:
					print("Error retrieving game id " + game_id +
						" for region " + api.default_region)
					print(sys.exc_info()[0])
					print(sys.exc_info()[1])
					continue

				if match_data["matchType"] != "MATCHED_GAME":
					print("Skipping non matched game")
					continue # Skip any non-matched games

				try:
					internal_match_id = store_match_data(c, match_data)
				except:
					print("Uncaught error for store match data", sys.exc_info()[0])
					print(sys.exc_info()[1])
					continue
				if not internal_match_id:
					continue

				if match_data["teams"][0]["bans"]:
					bans = match_data["teams"][0]["bans"]
					if match_data["teams"][1]["bans"]:
						bans += match_data["teams"][1]["bans"]
					try:
						store_ban_data(c, bans, internal_match_id)
					except:
						print("Uncaught error for store ban data", sys.exc_info()[0])
						print(sys.exc_info()[1])
						continue


				for player in match_data["participants"]:
					try:
						store_player_data(c, player, match_data, internal_match_id)
					except:
						print("Uncaught error for store player data", sys.exc_info()[0])
						print(sys.exc_info()[1])

			except:
				print("Uncaught error for game processing", sys.exc_info()[0])
				print(sys.exc_info()[1])


		api.process_queue = []




conn.commit()
c.close()
