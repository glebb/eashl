import json
import pymongo
from pymongo.errors import DuplicateKeyError
import urllib

from pymemcache.client.base import Client

from settings import *
from storage import stats_for, update_team, get_club_personas

#from server import app

client = pymongo.MongoClient()
db = client.eashl

memcacheclient = Client(('localhost', 11211))

def get_team(club_id):
    '''Get team name. Fetch via http if not stored'''
    result = db.clubs.find_one({"_id": club_id})
    if not result:
        result = update_team(club_id)
    return result


def get_players(data, club):
    '''Extract player data from a game data entry. Fetch missing name via http if necessary.'''
    result = {}
    for player in data:
        temp = db.personas.find_one({"_id": player})
        if not temp:
            if 'details' in data[player]:
                name = data[player]['details']['personaName']
            else:
                players = get_club_personas(club)
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
