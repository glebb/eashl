import pymongo
from bson.code import Code

from settings import *

client = pymongo.MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl


def get_map_function(position, p_class=False):
    '''Javascript map function for mongodb for fetching player data by position.'''
    f = "function () {"
    f += "  var home_team = '" + HOME_TEAM + "';"
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
                  "  entry={'games':0, 'wins':0, 'sktakeaways':0, 'skgiveaways':0, 'skgoals':0, 'skassists': 0, 'skshots': 0, 'skhits': 0, 'skplusmin': 0, 'skpim':0 };"
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
                  "  }"
                  "  return entry;"
                  "}")
    return reduce


def format_player_data(collection, p_class=False):
    '''Format and count averages for data produced by map reduce'''
    plist = []
    for player in collection:
        if player['value']['games'] < 10:
            continue
        temp = {}
        temp['id'] = player['_id']
        games = player['value']['games']

        winpct = player['value']['wins'] / games * 100
        takeawayavg = float(player['value']['sktakeaways']) / games
        giveawayavg = float(player['value']['skgiveaways']) / games
        goalsavg = float(player['value']['skgoals']) / games
        assistsavg = float(player['value']['skassists']) / games
        shotsavg = float(player['value']['skshots']) / games
        hitsavg = float(player['value']['skhits']) / games
        plusminustotal = int(player['value']['skplusmin'])
        penaltiesavg = float(player['value']['skpim']) / games

        temp['winpct'] = "{0:.2f}".format(winpct)
        temp['giveawayavg'] = "{0:.2f}".format(giveawayavg)
        temp['takeawayavg'] = "{0:.2f}".format(takeawayavg)
        temp['goalsavg'] = "{0:.2f}".format(goalsavg)
        temp['assistsavg'] = "{0:.2f}".format(assistsavg)
        temp['hitsavg'] = "{0:.2f}".format(hitsavg)
        temp['shotsavg'] = "{0:.2f}".format(shotsavg)
        temp['plusminustotal'] = plusminustotal
        temp['penaltiesavg'] = "{0:.1f}".format(penaltiesavg)

        temp['games'] = "{0:.0f}".format(player['value']['games'])
        if p_class:
            temp['name'] = CLASSES[player["_id"]]
        else:
            temp['name'] = db.personas.find_one(
                {"_id": player["_id"]})['personaname']
        plist.append(temp)
    plist.sort(key=lambda b: float(b['winpct']), reverse=True)
    return plist
