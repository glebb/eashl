import json
import pymongo
from pymongo.errors import DuplicateKeyError
import urllib

from pymemcache.client.base import Client

from settings import *
import data_handling

client = pymongo.MongoClient()
db = client.eashl

memcacheclient = Client(('localhost', 11211))

def stats_for(game, entry, us=HOME_TEAM):
    '''Get stats for a game, fetches data via http if not available otherwise.'''
    for club in game['clubs']:
        if club == us:
            entry['us'] = data_handling.get_team(club)['name']
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
            entry['them'] = data_handling.get_team(club)['name']
            entry['them_goals'] = game['clubs'][club]['score']


def get_player_stats(player_id, club_id):
    '''Fetch data for single player via http. Store in memcached.'''
    result = memcacheclient.get('player_' + player_id)
    if result:
        return result

    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
        PLATFORM + "/clubs/" + club_id + "/members/" + player_id + "/stats"
    # app.logger.debug(url)
    response = urllib.urlopen(url)
    temp = json.loads(response.read())
    player = temp['raw'][player_id]
    memcacheclient.set('player_' + player_id, player, 60 * 5)
    return player


def get_club_personas(club_id):
    '''Fetch personaname for a player. Fetch directly via http. Store in mongodb.'''
    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
        PLATFORM + "/clubs/" + club_id + "/members"
    personas = {}
    # app.logger.debug(url)
    response = urllib.urlopen(url)
    try:
        temp = json.loads(response.read())
    except ValueError:
        return personas
    for player in temp['raw'][0]:
        person = {"personaname": temp['raw'][0][player]['name'], "_id": player}
        personas[player] = person
        try:
            db.personas.insert_one(person)
        except DuplicateKeyError:
            pass
    return personas


def update_team(club_id):
    '''Fetch team name via http. Store in mongodb.'''
    url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
        PLATFORM + "/clubs/" + club_id + "/info"
    # app.logger.debug(url)
    response = urllib.urlopen(url)
    try:
        temp = json.loads(response.read())
        name = temp['raw'][0]['name']
    except:
        name = "TEAM id:" + club_id + " does not exist anymore"
    result = {"_id": club_id, "name": name}
    db.clubs.insert_one(result)
    return result
