import sys, time
sys.path.insert(0,'..')

import urllib, json

import settings
from service import game as gameservice
from repository import mongo

def get_club_personas(club_id):
    '''Fetch personaname for a player. Fetch directly via http. Store in mongodb.'''
    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
        settings.PLATFORM + "/clubs/" + club_id + "/members"
    personas = {}
    response = urllib.urlopen(url)
    try:
        temp = json.loads(response.read())
    except ValueError:
        return personas
    for player in temp['raw'][0]:
        person = {"personaname": temp['raw'][0][player]['name'], "_id": player}
        personas[player] = person
        '''try:
            db.personas.insert_one(person)
        except DuplicateKeyError:
            pass'''
    return personas

def get_team_stats(team_id, team_name):
    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
        settings.PLATFORM + "/clubs/" + team_id + "/stats"
    response = urllib.urlopen(url)
    temp = json.loads(response.read())
    entry = {}
    entry['stats'] = json.dumps(
        temp['raw'][team_id], indent=2, sort_keys=True)
    entry['name'] = team_name #temp['raw'][team_id]['clubname'] #mongo.get_team(team_id)['name']
    entry['data'] = temp['raw'][team_id]
    return entry

def get_team_matches(team_id):
    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + settings.PLATFORM + \
        "/clubs/" + team_id + "/matches?match_type=gameType5&matches_returned=5"
    response = urllib.urlopen(url)
    temp = json.loads(response.read())['raw']
    games = []
    for game in temp:
        item = {}
        item['id'] = temp[game]['matchId']
        item['time'] = time.strftime(
            "%d.%m.%y %H:%M", time.localtime(int(temp[game]['timestamp'])))
        gameservice.stats_for(temp[game], item, mongo, team_id)
        games.append(item)
    return games

def get_player_stats(ids):
    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
        settings.PLATFORM + "/clubs/" + settings.HOME_TEAM + "/members/" + ids + "/stats"
    response = urllib.urlopen(url)
    players = json.loads(response.read())['raw']
    return players
