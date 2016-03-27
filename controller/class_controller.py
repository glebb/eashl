import pymongo

from flask import (render_template)

from storage import get_club_personas
from mapreduce import *
from settings import *

client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl

from flask import Blueprint

class_controller = Blueprint('class_controller', __name__)

@class_controller.route('/classes/')
@class_controller.route('/classes')
def show_classes():
    '''Show player class data for HOME_TEAM'''
    centers = db.our_games.map_reduce(get_map_function(
        "4", p_class=True), get_reduce_function("4"), "centers").find()
    centers = format_player_data(centers, p_class=True)
    lws = db.our_games.map_reduce(get_map_function(
        "3", p_class=True), get_reduce_function("3"), "lws").find()
    lws = format_player_data(lws, p_class=True)
    defenders = db.our_games.map_reduce(get_map_function(
        "1", p_class=True), get_reduce_function("1"), "defs").find()
    defenders = format_player_data(defenders, p_class=True)
    rws = db.our_games.map_reduce(get_map_function(
        "5", p_class=True), get_reduce_function("5"), "rws").find()
    rws = format_player_data(rws, p_class=True)

    return render_template('show_classes.html', data=PLAYERDATA, defenders=defenders, lws=lws, centers=centers, rws=rws)
