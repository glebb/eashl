import sys
sys.path.insert(0,'..')

from flask import (render_template, Blueprint, request)

import settings

from service import team
from repository import memcached, http

team_controller = Blueprint('team_controller', __name__)

@team_controller.route('/team/<team_id>')
@team_controller.route('/team/')
@team_controller.route('/team')
def show_team(team_id=settings.HOME_TEAM):
    team_name = request.args.get('name') or settings.HOME_TEAM_NAME
    stats = team.get_stats(team_id, team_name, memcached, http)
    games = team.get_matches(team_id, memcached, http)
    return render_template('show_team.html', entries=stats, games=games, home_team=(team_id == settings.HOME_TEAM))
