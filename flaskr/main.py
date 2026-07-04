import datetime
from flask import Blueprint, redirect, url_for, current_app, session, request

from logging import getLogger
logger = getLogger(__name__)

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('signup.root'))


@bp.route('/healthz', methods=['GET'])
def healthz():
    return "ok", 200


@bp.route('/login', methods=['GET'])
def login():
    # If flask is in debug mode, make the login button login automatically as a test user!
    if current_app.debug:
        session["login_data"] = {
            'provider': 'test',
            'unique_username': "TestUser1",
            'email': "testuser1@email.com",
            'preferred_username': "User1",
            'expires_at': (datetime.datetime.now() + datetime.timedelta(minutes=5)).timestamp(),
            'roles': ['role1', 'role2']
        }
        return redirect(request.args.get('after_login_redirect', '/'))

    return redirect('/login')  # Redirects to the root site, not in this repo!
    # This handles login for us, and will return us back here :)


@bp.route('/user', methods=['GET'])
def user():
    return redirect('/user')  # Redirects to the root site, not in this repo!
    # This handles user settings for us, and will return us back here :)


@bp.route('/logout')
def logout():
    return redirect('/logout')  # Redirects to the root site, not in this repo!
    # This handles logout for us, and will return us back here :)
