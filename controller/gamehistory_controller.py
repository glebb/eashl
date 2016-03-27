import time

import pymongo
from flask import (render_template)

from data_handling import *
from settings import *


client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl

from flask import Blueprint

gamehistory_controller = Blueprint('gamehistory_controller', __name__)

@gamehistory_controller.route('/')
def show_games():
    '''Main view, display match history'''
    entries = []
    cursor = db.our_games.find().sort("timestamp", pymongo.DESCENDING)
    for game in cursor:
        entry = {}
        entry['id'] = game['matchId']
        entry['time'] = time.strftime(
            "%d.%m.%y %H:%M", time.localtime(int(game['timestamp'])))
        stats_for(game, entry)
        players = ""
        for player in get_players(game['players'][HOME_TEAM], HOME_TEAM):
            players += player + ", "
        players = players[:-2]
        entry['players'] = players
        entries.append(entry)
    return render_template('show_games.html', games=entries, id=HOME_TEAM)
