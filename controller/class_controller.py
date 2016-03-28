import sys
sys.path.insert(0,'..')

from flask import (render_template)

import settings
from service import player
from repository import mongo

from flask import Blueprint

class_controller = Blueprint('class_controller', __name__)

@class_controller.route('/classes/')
@class_controller.route('/classes')
def show_classes():
    '''Show player class data for HOME_TEAM'''
    positions = player.get_positions(mongo, True)
    return render_template('show_classes.html', data=settings.PLAYERDATA, positions=positions)
