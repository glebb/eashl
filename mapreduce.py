import pymongo
from bson.code import Code

from settings import *


client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl

def get_map_function(position):
    '''Javascript map function for mongodb for fetching player data by position.'''
    reduce = Code("function () {"
                  "  var res = 0;"
                  "  if (parseInt(this['clubs']['219']['goals']) > parseInt(this['clubs']['219']['goalsAgainst'])) res = 1;"
                  "  for (var key in this.players['219']) {"
                  "    if (this.players['219'].hasOwnProperty(key)) {"
                  "       if (this.players['219'][key].position == '" +
                  position + "'){"
                  "          entry = {};"
                  "          entry['games'] = 1;"
                  "          entry['wins'] = res;"
                  "          entry['skgiveaways'] = parseInt(this.players['219'][key].skgiveaways);"
                  "          entry['sktakeaways'] = parseInt(this.players['219'][key].sktakeaways);"
                  "          entry['skgoals'] = parseInt(this.players['219'][key].skgoals);"
                  "          entry['skassists'] = parseInt(this.players['219'][key].skassists);"
                  "          entry['skplusmin'] = parseInt(this.players['219'][key].skplusmin);"
                  "          entry['skpim'] = parseInt(this.players['219'][key].skpim);"
                  "          emit(key, entry);"
                  "       }"
                  "    }"
                  "  }"
                  "}")
    return reduce


def get_reduce_function(position):
    '''Javascript reduce function for mongodb for aggregating player data by position.'''
    reduce = Code("function (key, values) {"
                  "  entry={'games':0, 'wins':0, 'sktakeaways':0, 'skgiveaways':0, 'skgoals':0, 'skassists': 0, 'skplusmin': 0, 'skpim':0 };"
                  "  for (var i = 0; i<values.length; i++) {"
                  "    entry['games'] += values[i]['games'];"
                  "    entry['wins'] += values[i]['wins'];"
                  "    entry['sktakeaways'] += values[i]['sktakeaways'];"
                  "    entry['skgiveaways'] += values[i]['skgiveaways'];"
                  "    entry['skgoals'] += values[i]['skgoals'];"
                  "    entry['skassists'] += values[i]['skassists'];"
                  "    entry['skplusmin'] += values[i]['skplusmin'];"
                  "    entry['skpim'] += values[i]['skpim'];"
                  "  }"
                  "  return entry;"
                  "}")
    return reduce


def format_player_data(collection):
    '''Format and count averages for data produced by map reduce'''
    plist = []
    for player in collection:
        temp = {}
        temp['id'] = player['_id']
        games = player['value']['games']

        winpct = player['value']['wins'] / games * 100
        takeawayavg = float(player['value']['sktakeaways']) / games
        giveawayavg = float(player['value']['skgiveaways']) / games
        goalsavg = float(player['value']['skgoals']) / games
        assistsavg = float(player['value']['skassists']) / games
        plusminusavg = float(player['value']['skplusmin']) / games
        penaltiesavg = float(player['value']['skpim']) / games

        temp['winpct'] = "{0:.1f}".format(winpct)
        temp['giveawayavg'] = "{0:.1f}".format(giveawayavg)
        temp['takeawayavg'] = "{0:.1f}".format(takeawayavg)
        temp['goalsavg'] = "{0:.1f}".format(goalsavg)
        temp['assistsavg'] = "{0:.1f}".format(assistsavg)
        temp['plusminusavg'] = "{0:.1f}".format(plusminusavg)
        temp['penaltiesavg'] = "{0:.1f}".format(penaltiesavg)

        temp['games'] = "{0:.0f}".format(player['value']['games'])
        temp['name'] = db.personas.find_one(
            {"_id": player["_id"]})['personaname']
        plist.append(temp)
    plist.sort(key=lambda b: float(b['winpct']), reverse=True)
    return plist
