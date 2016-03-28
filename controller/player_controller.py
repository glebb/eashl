import sys
sys.path.insert(0,'..')


from flask import (render_template)


from service import player
import settings
from repository import memcached, http, mongo

from flask import Blueprint

player_controller = Blueprint('player_controller', __name__)

@player_controller.route('/players/')
@player_controller.route('/players')
def show_players():
    '''Show player data for HOME_TEAM'''
    players = player.get_players(memcached, http, mongo)
    positions = player.get_positions(mongo, False)
    return render_template('show_players.html', players=players, data=settings.PLAYERDATA, positions=positions)
