DELETE FROM Match
WHERE NOT EXISTS(SELECT NULL
FROM MatchSummoner WHERE MatchSummoner.InternalMatchId = Match.Id)
