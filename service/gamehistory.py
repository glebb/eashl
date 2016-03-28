import time
import sys
sys.path.insert(0,'..')

from service import game as gameservice
import settings

def get_games(game_repository, live_repository):
    entries = []
    for game in game_repository.get_games():
        entry = {}
        entry['id'] = game['matchId']
        entry['time'] = time.strftime(
            "%d.%m.%y %H:%M", time.localtime(int(game['timestamp'])))
        gameservice.stats_for(game, entry, game_repository)
        players = ""
        for player in gameservice.get_players(game['players'][settings.HOME_TEAM], settings.HOME_TEAM, game_repository, live_repository):
            players += player + ", "
        players = players[:-2]
        entry['players'] = players
        entries.append(entry)
    return entries
