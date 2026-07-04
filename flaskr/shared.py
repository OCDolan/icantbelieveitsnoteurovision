import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

from flask import session, redirect, render_template, request, url_for

from logging import getLogger

logger = getLogger(__name__)


class LoginInfo2:

    # Thin wrapper around session's login_data. Checks for user valid-ness before returning
    # Yes I know i should turn this in to a dataclass also

    @classmethod
    def retrieve(cls, param=None):
        if 'login_data' not in session:
            logger.info("No login_data found in session")
            return {}
        login_data = session['login_data']
        # For a user to login, they have to pass some basic checks...
        try:
            info = {
                'provider': login_data['provider'],
                'unique_username': login_data['unique_username'],
                # We only trust that the unique username is unique within a single identity provider
                # (for example, the user "Dylan" could exist on two identity providers with different users behind them)
                'globally_unique_username': login_data['provider'] + ':' + login_data['unique_username'],
                'email': login_data.get('email', None),
                'preferred_name': login_data.get('preferred_name', login_data['unique_username']),
                'time_until_expiry': datetime.fromtimestamp(login_data['expires_at']) - datetime.now()
            }
            info['roles'] = login_data.get('roles', [])
            info['time_until_expiry_pretty'] = f"{str(info['time_until_expiry']).split('.')[0]} (Hours Minutes Seconds)"

            is_not_expired = info['time_until_expiry'] > timedelta()
            if is_not_expired:
                # logger.info(
                #    f"Detected user {info['unique_username']} via {info['provider']} - "
                #    f"expires in {info['time_until_expiry_pretty']} - "
                #    f"Roles: {info['roles']}"
                # )
                logger.info(f"Detected user {info['unique_username']} via {info['provider']} - ")
                return info
            else:
                msg = f"Detected user {info['unique_username']} via {info['provider']} has expired login!"
                logger.warning(msg)
                return {}
        except Exception as e:
            msg = f"Unable to detect login state with login_data {session['login_data']}"
            logger.error(msg)
            return {}

    @classmethod
    def is_logged_in(cls):
        return True if cls.retrieve() else False

    @classmethod
    def get_roles(cls):
        return cls.retrieve().get('roles', [])

    @classmethod
    def role_check(cls, role):
        return role in cls.get_roles()

    @classmethod
    def logout(cls):
        if cls.is_logged_in():
            logger.warning(f"Logging out user {cls.retrieve()['globally_unique_username']}")
        session.pop('login_data')


def get_default_context():
    logger.warning("Getting default context...")
    return {
        "this_page_url": url_for(request.url_rule.endpoint),
        "this_page_url_external": url_for(request.url_rule.endpoint, _external=True),
        "li": LoginInfo2.retrieve(),
        "logged_in": LoginInfo2.is_logged_in(),
    }


def after_login_redirect():
    # Returns the user back where they came from before they had to do a login!
    after_login_redirect = session.pop("after_login_redirect", None)
    if after_login_redirect:
        logger.info(f"after_login_redirect found in session, redirecting to {after_login_redirect}")
    else:
        after_login_redirect = url_for('main.user')
        logger.info(f"after_login_redirect missing!")
    return redirect(after_login_redirect)


def render_error_page(error_message, http_status=500):
    context = get_default_context()
    context['error_message'] = error_message
    return render_template('error.html', **context), http_status
