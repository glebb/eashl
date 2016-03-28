import sys
sys.path.insert(0,'..')

from pymemcache.client.base import Client

memcacheclient = Client(('localhost', 11211))

def get_team_stats(team_id):
    return memcacheclient.get('team_stats_' + team_id)

def set_team_stats(team_id, entry):
    memcacheclient.set('team_stats_' + team_id, entry, 60 * 60)

def get_team_matches(team_id):
    return memcacheclient.get('team_matches_' + team_id)

def set_team_matches(team_id, entry):
    memcacheclient.set('team_matches_' + team_id, entry, 60)

def get_player_stats():
    return memcacheclient.get('playerstats')

def set_player_stats(player_stats):
    memcacheclient.set('playerstats', player_stats, 60 * 2)    

def get_players():
    return memcacheclient.get('players')

def set_players(players):
    memcacheclient.set('players', players, 60 * 60)
