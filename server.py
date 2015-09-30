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

app = Flask(__name__)
app.debug = DEBUG

client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl


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

@app.route('/')
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


@app.route('/game/<id>')
@app.route('/game/<id>/')
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
            entry['our_players'] = json.dumps(get_players(
                game['players'][club], club), indent=2, sort_keys=True)
        else:
            entry['their_players'] = json.dumps(get_players(
                game['players'][club], club), indent=2, sort_keys=True)
    return render_template('show_game.html', entries=entry)


@app.route('/players')
@app.route('/players/')
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

    return render_template('show_players.html', players=players, data=PLAYERDATA, defenders=defenders, lws=lws, centers=centers, rws=rws)


@app.route('/team/<id>')
@app.route('/team/')
@app.route('/team')
def show_team(id=HOME_TEAM):
    entry = memcacheclient.get('team_stats_' + id)
    if not entry:
        url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + \
            PLATFORM + "/clubs/" + id + "/stats"
        app.logger.debug(url)
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
        app.logger.debug(url)
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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
