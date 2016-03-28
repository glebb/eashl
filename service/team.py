import sys
import json
sys.path.insert(0,'..')

def get_stats(team_id, team_name, cache_repository, http_repository):
    stats = cache_repository.get_team_stats(team_id)
    if not stats:
        stats = http_repository.get_team_stats(team_id, team_name)
        cache_repository.set_team_stats(team_id, json.dumps(stats))
    else:
        stats = json.loads(stats)
    return stats

def get_matches(team_id, cache_repository, http_repository):
    games = cache_repository.get_team_matches(team_id)
    if not games:
        games = http_repository.get_team_matches(team_id)
        cache_repository.set_team_matches(team_id, json.dumps(games))
    else:
        games = json.loads(games)
    games.sort(key=lambda b: b['time'], reverse=True)
    return games
