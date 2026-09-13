import os
import json
from pathlib import Path

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .shared import get_default_context, render_error_page, LoginInfo2
from .library_eurovision import Entry, Eurovision, BASEPATH

from logging import getLogger

logger = getLogger(__name__)

bp = Blueprint('vote', __name__, url_prefix='/vote')


def get_jury_vote_filename(vote_type: str = "") -> Path:
    """vote_type should be one of jury, postcard, """
    entry = Eurovision.get_entry_by_user(LoginInfo2.retrieve()['preferred_name'])
    return Path(BASEPATH, 'points', f'points_jury_{entry.country}.json')


def get_votable_entries() -> list[Entry]:
    """All of the entries that you are allowed to vote on"""
    contestants = Eurovision.get_contestants()
    my_entry: Entry = Eurovision.get_entry_by_user(LoginInfo2.retrieve()['preferred_name'])
    return [c for c in contestants if c.country != my_entry.country]


@bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('vote.jury'))


@bp.route('/jury', methods=['GET'])
def jury():
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)
    if not Eurovision.is_voting_open():
        return render_error_page("Voting is not open yet!", 401)

    # If number of entries are 4...
    # You can't vote for yourself...
    contestants = get_votable_entries()  # This would be 3
    # and you can't give any points to last place...
    votes_num = len(contestants) - 1
    # Therefore you can only give 12 and 10 points out...
    # This gives you a votes_num of 2
    # And ofcourse you cant vote for more than 6, since you only have 12,10,8,6,4,2 points to give
    votes_num = min(votes_num, 6)
    # So in the example above, points_nums_available = [12,10]
    points_nums_available = [12,10,8,6,4,2][:votes_num]

    context = get_default_context()
    if not os.path.exists(get_jury_vote_filename()):
        with open(get_jury_vote_filename(), 'w') as f:
            json.dump({}, f)
    context['current_votes'] = json.load(open(get_jury_vote_filename()))
    context['voting_disabled'] = 'false'
    context['points_nums_available'] = points_nums_available
    context['countries'] = [c.country for c in contestants]
    return render_template("jury.html", **context)


@bp.route('/jury_submit', methods=['POST'])
def jury_submit():
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)
    if not Eurovision.is_voting_open():
        return render_error_page("Voting is not open yet!", 401)

    points = {}
    for n in [12,10,8,6,4,2]:
        receiving_country = request.form.get(f'points_{n}', None)
        if receiving_country:
            points[receiving_country] = n

    if len(points.keys()) != (len(get_votable_entries()) - 1):
        return render_error_page("Unfinished or duplicate selections detected", 401)

    if os.path.exists(get_jury_vote_filename()):
        data = json.load(open(get_jury_vote_filename()))
        if data.get('announce', False) or data.get('announce_12', False):
            return render_error_page("Can't change points or duplicate selections detected", 401)

    with open(get_jury_vote_filename(), 'w') as f:
        json.dump(points, f)
    return "ok"


@bp.route('/jury_announce', methods=['POST'])
def jury_announce():
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)

    data = json.load(open(get_jury_vote_filename()))
    data['announce'] = True
    with open(get_jury_vote_filename(), 'w') as f:
        json.dump(data, f)
    return "ok"


@bp.route('/jury_announce_12', methods=['POST'])
def jury_announce_12():
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)

    data = json.load(open(get_jury_vote_filename()))
    data['announce_12'] = True
    with open(get_jury_vote_filename(), 'w') as f:
        json.dump(data, f)
    return "ok"

