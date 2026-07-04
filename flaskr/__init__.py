import os
import uuid

import flask
from flask import Flask
from flask_session.redis import RedisSessionInterface
from redis import Redis
from werkzeug.datastructures import Authorization

from werkzeug.middleware.proxy_fix import ProxyFix

from . import main, signup, vote


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

    app.register_blueprint(main.bp)
    app.register_blueprint(signup.bp)
    app.register_blueprint(vote.bp)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    if 'REDIS_HOST' in os.environ:
        redis_host = os.environ['REDIS_HOST']
        redis_port = int(os.environ.get('REDIS_PORT', '6379'))
        redis_password = os.environ['REDIS_PASSWORD']
        redis_client = Redis(host=redis_host, port=redis_port, password=redis_password)
        app.session_interface = RedisSessionInterface(app, client=redis_client)

    if app.debug:
        app.config["SECRET_KEY"] = "test"

    return app
