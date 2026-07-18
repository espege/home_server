#!/usr/bin/env python
"""Entry point for the Song Search App"""
import os
from app import create_app

app = create_app()


def create_gunicorn_app():
    return create_app()


if __name__ == "__main__":
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='127.0.0.1', port=5000, use_reloader=False)
