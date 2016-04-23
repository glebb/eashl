import sys, time
import json
sys.path.insert(0,'..')

import settings

def _count_averages(players):
    temp = {}
    for player in players:
        temp[player] = {}
        for key in players[player]:
            temp[player][key] = players[player][key]
            if key in ('skgoals', 'skassists', 'skpoints' , 'skhits', 'skshots'):
                temp[player][key+'avg'] = float("{0:.2f}".format(float(players[player][key]) / int(players[player]['totalgp'])))
    return temp

def _format_player_data(collection, game_repository, p_class=False):
    '''Format and count averages for data produced by map reduce'''
    plist = []
    for player in collection:
        if player['value']['games'] < settings.MIN_GAMES_TO_SHOW_IN_STATS:
            continue

        temp = {}
        temp['id'] = player['_id']
        games = player['value']['games']

        winpct = player['value']['wins'] / games * 100
        takeawayavg = float(player['value']['sktakeaways']) / games
        giveawayavg = float(player['value']['skgiveaways']) / games
        goalsavg = float(player['value']['skgoals']) / games
        assistsavg = float(player['value']['skassists']) / games
        shotsavg = float(player['value']['skshots']) / games
        hitsavg = float(player['value']['skhits']) / games
        plusminustotal = int(player['value']['skplusmin'])
        penaltiesavg = float(player['value']['skpim']) / games

        temp['winpct'] = "{0:.2f}".format(winpct)
        temp['giveawayavg'] = "{0:.2f}".format(giveawayavg)
        temp['takeawayavg'] = "{0:.2f}".format(takeawayavg)
        temp['goalsavg'] = "{0:.2f}".format(goalsavg)
        temp['assistsavg'] = "{0:.2f}".format(assistsavg)
        temp['hitsavg'] = "{0:.2f}".format(hitsavg)
        temp['shotsavg'] = "{0:.2f}".format(shotsavg)
        temp['plusminustotal'] = plusminustotal
        temp['penaltiesavg'] = "{0:.1f}".format(penaltiesavg)

        temp['games'] = "{0:.0f}".format(player['value']['games'])
        if p_class:
            temp['name'] = settings.CLASSES[player["_id"]]
        else:
            temp['name'] = player['value']['personaName']
        plist.append(temp)
    plist.sort(key=lambda b: float(b['winpct']), reverse=True)
    return plist

def get_players(cache_repository, live_repository, game_repository):
    player_stats = cache_repository.get_player_stats()
    if not player_stats:
        players = cache_repository.get_players()
        if not players:
            players = live_repository.get_club_personas(settings.HOME_TEAM)
            cache_repository.set_players(json.dumps(players))
        else:
            players = json.loads(players)
        ids = ""
        for player in players:
            ids += players[player]["_id"] + ","
        player_stats = live_repository.get_player_stats(ids)
        player_stats = _count_averages(player_stats)
        for player in player_stats:
            result = game_repository.get_player(player)
            if result:
                player_stats[player]['personaname'] = result['personaname']
        cache_repository.set_player_stats(json.dumps(player_stats))
    else:
        player_stats = json.loads(player_stats)
    return player_stats

def get_positions(game_repository, p_class):
    positions = {}
    positions['centers'] = _format_player_data(game_repository.get_centers(p_class), game_repository, p_class)
    positions['lws'] = _format_player_data(game_repository.get_lws(p_class), game_repository, p_class)
    positions['rws'] = _format_player_data(game_repository.get_rws(p_class), game_repository, p_class)
    positions['defenders'] = _format_player_data(game_repository.get_defenders(p_class), game_repository, p_class)
    return positions
