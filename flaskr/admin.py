import os
import uuid
import json
from pathlib import Path
from glob import glob

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, app, current_app, send_file
from werkzeug.utils import secure_filename

from .shared import get_default_context, render_error_page, LoginInfo2
from .library_eurovision import Entry, Eurovision, BASEPATH

from logging import getLogger

logger = getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/', methods=['GET'])
def root():
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)

    context = get_default_context()
    return render_template("admin_panel.html", **context)


@bp.route('/api/is_voting_open', methods=['GET', 'POST'])
def api_voting_open():
    is_voting_open = Eurovision.is_voting_open()
    if request.method == 'GET':
        return {'value': is_voting_open}
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)
    Eurovision.set_is_voting_open(not is_voting_open)  # Just toggle it
    return 'ok'

@bp.route('/api/reset_jury_votes', methods=['POST'])
def reset_jury_votes():
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)
    Eurovision.un_announce_jury_vote()
    return 'ok'

@bp.route('/api/reset_public_votes', methods=['POST'])
def reset_public_votes():
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)
    Eurovision.reset_public_vote()
    return 'ok'

@bp.route('/points', methods=['GET'])
def points():
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)

    total_points: dict[str, int] = Eurovision.get_points()

    rendered_total_points = []
    for country, points_awarded in total_points.items():
        entry = Eurovision.get_entry_by_country(country)
        rendered_total_points.append({
            'id': country,
            'name': f"{country} - {entry.song_name}",
            'points': points_awarded,
            'flag_url': url_for('signup.entry_asset', filename=entry.flag_filename),
            'colour': entry.favourite_colour,
        })
    return rendered_total_points

@bp.route('/scoreboard', methods=['GET'])
def scoreboard():
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)

    context = get_default_context()
    return render_template("scoreboard.html", **context)
