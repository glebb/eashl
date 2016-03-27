import time

import pymongo
from flask import (render_template)

from data_handling import *
from settings import *

client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl


from flask import Blueprint

game_controller = Blueprint('game_controller', __name__)


@game_controller.route('/game/<id>/')
@game_controller.route('/game/<id>')
def show_game(id):
    '''Show statistic for a single game'''
    entry = {}
    game = db.our_games.find_one({"_id": int(id)})
    stats_for(game, entry)
    entry['id'] = game['matchId']
    entry['time'] = time.strftime(
        "%d.%m.%y %H:%M", time.localtime(int(game['timestamp'])))
    for club in game['clubs']:
        if club == HOME_TEAM:
            entry['our_players'] = get_players(
                game['players'][club], club)
        else:
            entry['their_players'] = get_players(
                game['players'][club], club)
    return render_template('show_game.html', entries=entry)
