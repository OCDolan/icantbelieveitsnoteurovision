import datetime
import random

from flask import Blueprint, redirect, url_for, current_app, session, request

from logging import getLogger

from flaskr.shared import LoginInfo2

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
    session['after_login_redirect'] = request.args.get('after_login_redirect', url_for('main.root'))

    # If flask is in debug mode, make the login button login automatically as a test user!
    if current_app.debug:
        user = random.choice(['TestUser1', 'TestUser2'])
        session["login_data"] = {
            'provider': 'test',
            'unique_username': user,
            'email': "testuser1@email.com",
            'preferred_username': user,
            'expires_at': (datetime.datetime.now() + datetime.timedelta(minutes=999)).timestamp(),
            'roles': ['euroadmin']
        }
        return redirect(session.pop('after_login_redirect'))

    return redirect(f'/login')
    # Redirects to the root site, not in this repo!
    # This handles login for us, and will return us back here :)


@bp.route('/user', methods=['GET'])
def user():
    return redirect('/user')  # Redirects to the root site, not in this repo!
    # This handles user settings for us, and will return us back here :)


@bp.route('/logout')
def logout():
    after_logout_redirect = request.args.get('after_login_redirect', url_for('main.root'))
    LoginInfo2.logout()
    return redirect(after_logout_redirect)
