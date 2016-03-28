import sys, time
sys.path.insert(0,'..')

import settings

def stats_for(game, entry, game_repository, us=settings.HOME_TEAM):
    '''Get stats for a game, fetches data via http if not available otherwise.'''
    for club in game['clubs']:
        if club == us:
            try:
                entry['us'] = game['clubs'][club]['details']['name']
            except:
                entry['us'] = 'Unknown'
            entry['us_id'] = club
            entry['us_goals'] = game['clubs'][club]['score']
            entry['us_memberstring'] = game['clubs'][club]['memberstring']
            if int(game['clubs'][club]['goals']) > int(game['clubs'][club]['goalsAgainst']):
                entry['result'] = "label label-success"
            elif int(game['clubs'][club]['goals']) < int(game['clubs'][club]['goalsAgainst']):
                entry['result'] = "label label-danger"
            else:
                entry['result'] = "label label-default"
        else:
            entry['them_id'] = club
            entry['them_memberstring'] = game['clubs'][club]['memberstring']
            try:
                entry['them'] = game['clubs'][club]['details']['name']
            except:
                entry['them'] = 'Unknown'
            entry['them_goals'] = game['clubs'][club]['score']

def get_players(data, club, game_repository, live_repository):
    '''Extract player data from a game data entry. Fetch missing name via http if necessary.'''
    result = {}
    for player in data:
        temp = game_repository.get_player(player)
        if not temp:
            if 'details' in data[player]:
                name = data[player]['details']['personaName']
            else:
                players = live_repository.get_club_personas(club)
                if player in players:
                    name = players[player]['personaname']
                else:
                    name = "Unknown"
        else:
            name = temp['personaname']
        result[name] = {}
        if 'details' in data[player]:
            del data[player]['details']
        for key, value in data[player].iteritems():
            if key == "class":
                try:
                    value = CLASSES[value]
                except:
                    pass
            result[name][key] = value
    return result

def get_game(game_id, game_repository, live_repository):
    entry = {}
    game = game_repository.get_game(game_id)
    stats_for(game, entry, game_repository)
    entry['id'] = game['matchId']
    entry['time'] = time.strftime(
        "%d.%m.%y %H:%M", time.localtime(int(game['timestamp'])))
    for club in game['clubs']:
        if club == settings.HOME_TEAM:
            entry['our_players'] = get_players(
                game['players'][club], club, game_repository, live_repository)
        else:
            entry['their_players'] = get_players(
                game['players'][club], club, game_repository, live_repository)
    return entry
