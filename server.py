import json
import time
import urllib

import pymongo
from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)

from data_handling import *
from storage import get_club_personas
from mapreduce import *
from settings import *

from controller.class_controller import class_controller
from controller.game_controller import game_controller
from controller.gamehistory_controller import gamehistory_controller
from controller.player_controller import player_controller
from controller.team_controller import team_controller

client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl


app = Flask(__name__)
app.debug = DEBUG

app.register_blueprint(class_controller)
app.register_blueprint(game_controller)
app.register_blueprint(gamehistory_controller)
app.register_blueprint(player_controller)
app.register_blueprint(team_controller)




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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
