#!/bin/bash

set -e

cd $(dirname $0)
export VIRTUAL_ENV="/home/invenflask/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
unset PYTHON_HOME
exec venv/bin/gunicorn -w 1 --bind 0.0.0.0:8000 wsgi:app 2>&1 | /usr/bin/logger -t invenflask
