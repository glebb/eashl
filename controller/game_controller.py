import sys
sys.path.insert(0,'..')

from flask import (render_template)

from service import game as gameservice
from repository import mongo, http

from flask import Blueprint

game_controller = Blueprint('game_controller', __name__)


@game_controller.route('/game/<game_id>/')
@game_controller.route('/game/<game_id>')
def show_game(game_id):
    '''Show statistic for a single game'''
    game = gameservice.get_game(game_id, mongo, http)
    return render_template('show_game.html', entries=game)
