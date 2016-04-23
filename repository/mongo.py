import sys
sys.path.insert(0,'..')

import pymongo
from bson.code import Code

import settings

client = pymongo.MongoClient()
client.eashl.authenticate(settings.MONGODBUSER, settings.MONGODBPWD)
db = client.eashl

def get_map_function(position, p_class=False):
    '''Javascript map function for mongodb for fetching player data by position.'''
    f = "function () {"
    f += "  var home_team = '" + settings.HOME_TEAM + "';"
    f += "  var res = 0;" \
        "  if (parseInt(this['clubs'][home_team]['goals']) >  parseInt(this['clubs'][home_team]['goalsAgainst'])) res = 1;" \
        "  for (var key in this.players[home_team]) {" \
        "    if (this.players[home_team].hasOwnProperty(key)) {" \
        "       if (this.players[home_team][key].position == '" + position + "'){" \
        "          entry = {};" \
        "          entry['games'] = 1;" \
        "          entry['wins'] = res;" \
        "          entry['skgiveaways'] = parseInt(this.players[home_team][key].skgiveaways);" \
        "          entry['sktakeaways'] = parseInt(this.players[home_team][key].sktakeaways);" \
        "          entry['skgoals'] = parseInt(this.players[home_team][key].skgoals);" \
        "          var name = this.players[home_team][key]['details'].personaName;" \
        "          if (name) entry['personaName'] = name;" \
        "          entry['skassists'] = parseInt(this.players[home_team][key].skassists);" \
        "          entry['skshots'] = parseInt(this.players[home_team][key].skshots);" \
        "          entry['skhits'] = parseInt(this.players[home_team][key].skhits);" \
        "          entry['skplusmin'] = parseInt(this.players[home_team][key].skplusmin);" \
        "          entry['skpim'] = parseInt(this.players[home_team][key].skpim);"
    if p_class:
        f += "          emit(this.players[home_team][key]['class'], entry);"
    else:
        f += "          emit(key, entry);"
    f += "       }" \
        "    }" \
        "  }" \
        "}"
    reduce = Code(f)
    return reduce


def get_reduce_function(position):
    '''Javascript reduce function for mongodb for aggregating player data by position.'''
    reduce = Code("function (key, values) {"
                  "  entry={'games':0, 'wins':0, 'sktakeaways':0, 'skgiveaways':0, 'skgoals':0, 'skassists': 0, 'skshots': 0, 'skhits': 0, 'skplusmin': 0, 'skpim':0};"
                  "  for (var i = 0; i<values.length; i++) {"
                  "    entry['games'] += values[i]['games'];"
                  "    entry['wins'] += values[i]['wins'];"
                  "    entry['sktakeaways'] += values[i]['sktakeaways'];"
                  "    entry['skgiveaways'] += values[i]['skgiveaways'];"
                  "    entry['skgoals'] += values[i]['skgoals'];"
                  "    entry['skassists'] += values[i]['skassists'];"
                  "    entry['skshots'] += values[i]['skshots'];"
                  "    entry['skhits'] += values[i]['skhits'];"
                  "    entry['skplusmin'] += values[i]['skplusmin'];"
                  "    entry['skpim'] += values[i]['skpim'];"
                  "    if (values[i]['personaName']) entry['personaName'] = values[i]['personaName'];"
                  "  }"
                  "  return entry;"
                  "}")
    return reduce


def get_games():
    return db.our_games.find().sort("timestamp", pymongo.DESCENDING)

def get_team(club_id):
    return db.clubs.find_one({"_id": club_id})

def get_player(player):
    return db.personas.find_one({"_id": player})

def get_game(game_id):
    return db.our_games.find_one({"_id": int(game_id)})

def get_centers(p_class):
    return db.our_games.map_reduce(get_map_function(
        "4", p_class), get_reduce_function("4"), "centers").find()

def get_lws(p_class):
    return db.our_games.map_reduce(get_map_function(
        "3", p_class), get_reduce_function("3"), "lws").find()

def get_rws(p_class):
    return db.our_games.map_reduce(get_map_function(
        "5", p_class), get_reduce_function("5"), "rws").find()
def get_defenders(p_class):
    return db.our_games.map_reduce(get_map_function(
        "1", p_class), get_reduce_function("1"), "defs").find()
