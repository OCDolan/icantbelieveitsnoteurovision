#!/bin/sh
set -eu

python3 -m pip install --no-cache-dir -r requirements.txt
gunicorn --timeout 300 --reload -b 0.0.0.0:8080 --reload --reload-extra-file flaskr/templates -w 2 'flaskr:create_app()'
