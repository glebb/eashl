import json
import urllib

import pymongo
from flask import (render_template)

from data_handling import *
from storage import get_club_personas
from mapreduce import *
from settings import *


client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl

from flask import Blueprint

player_controller = Blueprint('player_controller', __name__)

def json_serializer(key, value):
    '''For memcached'''
    if type(value) == str:
        return value, 1
    return json.dumps(value), 2


def json_deserializer(key, value, flags):
    '''For memcached'''
    if flags == 1:
        return value
    if flags == 2:
        return json.loads(value)
    raise Exception("Unknown serialization format")


memcacheclient = Client(('localhost', 11211), serializer=json_serializer,
                        deserializer=json_deserializer)


@player_controller.route('/players/')
@player_controller.route('/players')
def show_players():
    '''Show player data for HOME_TEAM'''
    players = memcacheclient.get('playerstats')
    if not players:
        result = memcacheclient.get('players')
        if not result:
            result = get_club_personas(HOME_TEAM)
            memcacheclient.set('players', result, 60 * 60)
        ids = ""
        for player in result:
            ids += result[player]["_id"] + ","
        url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
            PLATFORM + "/clubs/" + HOME_TEAM + "/members/" + ids + "/stats"
        #app.logger.debug(url)
        response = urllib.urlopen(url)
        players = json.loads(response.read())['raw']
        memcacheclient.set('playerstats', players, 60 * 2)
    for player in players:
        result = db.personas.find_one({"_id": player})
        if result:
            players[player]['playername'] = result['personaname']

    players2 = count_averages(players)

    centers = db.our_games.map_reduce(get_map_function(
        "4"), get_reduce_function("4"), "centers").find()
    centers = format_player_data(centers)
    lws = db.our_games.map_reduce(get_map_function(
        "3"), get_reduce_function("3"), "lws").find()
    lws = format_player_data(lws)
    defenders = db.our_games.map_reduce(get_map_function(
        "1"), get_reduce_function("1"), "defs").find()
    defenders = format_player_data(defenders)
    rws = db.our_games.map_reduce(get_map_function(
        "5"), get_reduce_function("5"), "rws").find()
    rws = format_player_data(rws)

    return render_template('show_players.html', players=players2, data=PLAYERDATA, defenders=defenders, lws=lws, centers=centers, rws=rws)
