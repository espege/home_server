#!/bin/sh
python -m venv venv && sleep 1 && source venv/bin/activate
pip install -r requirements.txt
python3 /app/seed_db.py
# python3 run.py
gunicorn --bind 0.0.0.0:5000 "run:create_gunicorn_app()"
