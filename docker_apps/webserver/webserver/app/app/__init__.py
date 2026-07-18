from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config')

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from .routes.search import search_bp
    app.register_blueprint(search_bp)

    # Create database tables and reset stale schema if needed
    with app.app_context():
        from .models.song import Song

        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())
        expected_tables = {
            'songs',
            'composers',
            'interpreters',
            'media_links',
            'genres',
            'subgenres',
            'scores',
            'song_composers',
            'song_interpreters',
            'song_scores',
            'song_media_links',
        }
        if 'songs' in existing_tables:
            songs_columns = {c['name'] for c in inspector.get_columns('songs')}
            has_expected_schema = expected_tables.issubset(existing_tables) and 'subgenre_id' in songs_columns
        else:
            has_expected_schema = False

        if not has_expected_schema:
            db.drop_all()

        db.create_all()

        # Legacy data should be migrated with the one-time migration script.
        # Do not perform runtime migrations here.
        db.session.commit()

    return app
