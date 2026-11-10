#!/bin/sh
set -eu

if ! ./venv/bin/python -m pip --version >/dev/null 2>&1; then
    echo "No working pip found in venv; recreating virtualenv"
    python3 -m venv --clear venv
fi

./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python /app/seed_db.py
exec ./venv/bin/gunicorn --bind 0.0.0.0:5000 "run:create_gunicorn_app()"
