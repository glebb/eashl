# EA Sports NHL EASHL stats #
Web app to track stats for selected eashl team.

## Features ##
* Searchable match history with complete game statistics for selected team.
* Overall player statistics for selected team
* Position based statistics for selected team
* Current team statistics with list of recent matches for opponents

## Requirements ##
* Python 2.7
* MongoDB
* Memcached
* Python modules (via pip): Flask, pymongo, pymemcache, gunicorn
* cron

## How it works ##
The app uses public ea sports urls to fetch data in json format (check example_urls.txt). Depending on the data, it can be stored to mongodb collection for further processing and long term storing, to memcached server for short time cache storing, or served directly to end user. The data fetch process for long-term data (game history) can be configured to happen automatically via cron. The app itself is written in Python and runs as a Flask web app.

## Configuration ##
* Edit settings.py and set team id for the wanted team, platform (ps4, xboxone) and amount of matches to be fetched via "update_our_team_games.py".
* Replace static/logo.png with your selected team logo.
* Run update_our_team_games.py manually, and check that it populates mongodb database eashl and collection our_games. To get some history data, fetch e.g. 50 matches first. Afterwards, remember to set the configuration value to be less, as fetching large amount of match data takes a lot of time. 1-5 matches should be fine.
* Setup cron to run update_our_team_games.py e.g. once in 30 minutes. (e.g.
	*/30 * * * * /home/bodhi/apps/mhstats/update_our_team_games.py)
* Run the server.py via gunicorn. You can also configure it to run with Nginx (see start.sh)
* Try it out. It should be running on your host on port 5000. If it doesn't work, fix it and do a pull request.
