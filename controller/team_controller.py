
from flask import Blueprint
from flask import (render_template)

import json
import urllib
import time
import pymongo

from data_handling import *
from storage import get_club_personas
from mapreduce import *
from settings import *


client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl


team_controller = Blueprint('team_controller', __name__)


@team_controller.route('/team/<id>')
@team_controller.route('/team/')
@team_controller.route('/team')
def show_team(id=HOME_TEAM):
    entry = memcacheclient.get('team_stats_' + id)
    if not entry:
        url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
            PLATFORM + "/clubs/" + id + "/stats"
        response = urllib.urlopen(url)
        temp = json.loads(response.read())
        entry = {}
        try:
            entry['stats'] = json.dumps(
                temp['raw'][id], indent=2, sort_keys=True)
            entry['name'] = get_team(id)['name']
            entry['data'] = temp['raw'][id]
        except:
            entry['name'] = "Unknown"
            entry['stats'] = {}
            entry['data'] = {}
        memcacheclient.set('team_stats_' + id, entry, 60 * 60)

    games = memcacheclient.get('team_matches_' + id)
    if not games:
        url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + PLATFORM + \
            "/clubs/" + id + "/matches?match_type=gameType5&matches_returned=5"
        response = urllib.urlopen(url)
        temp = json.loads(response.read())['raw']
        games = []
        for game in temp:
            item = {}
            item['id'] = temp[game]['matchId']
            item['time'] = time.strftime(
                "%d.%m.%y %H:%M", time.localtime(int(temp[game]['timestamp'])))
            stats_for(temp[game], item, id)
            games.append(item)
        memcacheclient.set('team_matches_' + id, games, 60)
    games.sort(key=lambda b: b['time'], reverse=True)
    return render_template('show_team.html', entries=entry, games=games, home_team=(id == HOME_TEAM))
