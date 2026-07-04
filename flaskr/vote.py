import os
import uuid

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, app, current_app, send_file
from werkzeug.utils import secure_filename

from .shared import get_default_context, render_error_page, LoginInfo2
from .library_eurovision import Entry, Eurovision, BASEPATH

from logging import getLogger

logger = getLogger(__name__)


bp = Blueprint('vote', __name__, url_prefix='/vote')


@bp.route('/', methods=['GET'])
def root():
    raise NotImplementedError("Voting is not implemented yet. Please check back later.")
