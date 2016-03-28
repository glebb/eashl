import sys
sys.path.insert(0,'..')

from flask import (render_template, Blueprint)

from service import gamehistory
import settings
from repository import mongo, http


gamehistory_controller = Blueprint('gamehistory_controller', __name__)

@gamehistory_controller.route('/')
def show_games():
    '''Main view, display match history'''
    games = gamehistory.get_games(mongo, http)
    return render_template('show_games.html', games=games, id=settings.HOME_TEAM)
