#!/usr/bin/env python
import urllib
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from settings import *

url = "https://www.easports.com/iframe/nhl14proclubs/api/platforms/" + PLATFORM + \
    "/clubs/" + HOME_TEAM + "/matches?match_type=gameType5&matches_returned=" + FETCH_MATCHES
response = urllib.urlopen(url)
temp = json.loads(response.read())

client = MongoClient()
client.eashl.authenticate(MONGODBUSER, MONGODBPWD)
db = client.eashl

for key, value in temp['raw'].iteritems():
    value['_id'] = int(key)
    try:
        db.our_games.insert_one(value)
    except DuplicateKeyError:
        pass
