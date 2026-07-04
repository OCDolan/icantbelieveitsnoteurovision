import os
import uuid

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, app, current_app, send_file
from werkzeug.utils import secure_filename

from .shared import get_default_context, render_error_page, LoginInfo2
from .library_eurovision import Entry, Eurovision, BASEPATH

from logging import getLogger

logger = getLogger(__name__)


bp = Blueprint('signup', __name__, url_prefix='/signup')


@bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('signup.landing'))


@bp.route('/landing', methods=['GET'])
def landing():
    context = get_default_context()
    context['entries'] = Eurovision.get_entries()
    return render_template('landing.html', **context)


@bp.route('/entries', methods=['GET'])
def entries():
    if not LoginInfo2.role_check('euroadmin'):
        return render_error_page("You are not allowed to access this page.", 403)

    context = get_default_context()
    context['entries'] = Eurovision.get_entries()
    return render_template('entries.html', **context)


@bp.route('/entry', methods=['GET'])
def entry():
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)

    # Get the Entry, and check the owner!
    entry = Eurovision.get_entry_by_user(LoginInfo2.retrieve()['preferred_name'])

    context = get_default_context()
    context['entry'] = entry
    return render_template('entry.html', **context)


@bp.route('/entry/asset/<filename>', methods=['GET'])
def entry_asset(filename):
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)
    return send_file(os.path.join(BASEPATH, secure_filename(filename)))


@bp.route('/entry', methods=['POST'])
def entry_edit():
    if not LoginInfo2.is_logged_in():
        return render_error_page("Please login first!", 401)

    # Get the Entry, and check the owner!
    entry: Entry = Eurovision.get_entry_by_user(LoginInfo2.retrieve()['preferred_name'])
    entry.lazy_save = True  # MUST CALL save_awaiting_writes later!

    country = request.form.get('country')
    if country:
        entry.country = country

    song_name = request.form.get('song_name')
    if song_name:
        entry.song_name = song_name

    song_url = request.form.get('song_url')
    if song_url:
        entry.song_url = song_url
        entry.song_filename = None

    song_file = request.files.get('song_file', None)
    if song_file:
        ext = secure_filename(song_file.filename).split('.')[-1]
        song_filename = f"{uuid.uuid4()}.{ext}"
        song_file.save(os.path.join(BASEPATH, song_filename))
        entry.song_filename = song_filename
        entry.song_url = None

    postcard_url = request.form.get('postcard_url')
    if postcard_url:
        entry.postcard_url = postcard_url

    postcard_file = request.files.get('postcard_file', None)
    if postcard_file:
        ext = secure_filename(postcard_file.filename).split('.')[-1]
        postcard_filename = f"{uuid.uuid4()}.{ext}"
        postcard_file.save(os.path.join(BASEPATH, postcard_filename))
        entry.postcard_filename = postcard_filename

    flag_file = request.files.get('flag_file', None)
    if flag_file:
        ext = secure_filename(flag_file.filename).split('.')[-1]
        flag_filename = f"{uuid.uuid4()}.{ext}"
        flag_file.save(os.path.join(BASEPATH, flag_filename))
        entry.flag_filename = flag_filename

    favourite_colour = request.form.get('favourite_colour')
    if favourite_colour:
        entry.favourite_colour = favourite_colour

    entry.save_awaiting_writes()

    return redirect(url_for('signup.entry'))
