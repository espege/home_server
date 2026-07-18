import json
import os

from flask import Blueprint, abort, jsonify, render_template, request, send_from_directory

from app import db
from app.models.song import Genre, SubGenre, Song

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['GET'])
def index():
    genres = db.session.query(Genre.name).distinct().all()
    genre_list = sorted([name for (name,) in genres if name])
    subgenres = db.session.query(SubGenre.name).distinct().all()
    subgenre_list = sorted([name for (name,) in subgenres if name])
    return render_template('index.html', genres=genre_list, subgenres=subgenre_list)


@search_bp.route('/all', methods=['GET'])
def all():
    results = Song.query.all()
    return jsonify([song.get_metadata() for song in results])


@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    genre = request.args.get('genre', '')
    subgenre = request.args.get('subgenre', '')

    if genre:
        results = Song.query.join(Song.genre).filter(Genre.name == genre).all()
    elif subgenre:
        results = Song.query.join(Song.subgenre).filter(SubGenre.name == subgenre).all()
    elif query:
        results = Song.query.filter(Song.title.ilike(f'%{query}%')).all()
    else:
        results = Song.query.all()

    return jsonify([song.get_metadata() for song in sorted(results, key=lambda x: x.title)])


@search_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get all unique genres from database"""
    genres = db.session.query(Genre.name).distinct().all()
    genre_list = sorted([name for (name,) in genres if name])
    return jsonify({'genres': genre_list})


@search_bp.route('/add-song', methods=['POST'])
def add_song():
    """Add a new song to the database"""
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    existing = Song.query.filter_by(title=data['title']).first()
    if existing:
        return jsonify({'error': 'Song already exists'}), 409

    song = Song(
        title=data['title'],
    )

    db.session.add(song)
    db.session.flush()

    if data.get('genre'):
        song.add_genre(data['genre'])

    if data.get('subgenre'):
        song.add_subgenre(data['subgenre'])

    for composer_name in data.get('composers', []):
        if composer_name:
            song.add_composer(composer_name)

    for interpreter_name in data.get('interpreters', []):
        if interpreter_name:
            song.add_interpreter(interpreter_name)

    for media_link_url in data.get('media_links', []):
        if media_link_url:
            song.add_media_link(media_link_url)

    for score_data in data.get('scores', []):
        if score_data:
            song.add_score(score_data)

    db.session.commit()

    return jsonify(song.get_metadata()), 201


@search_bp.route('/song/<int:song_id>', methods=['GET'])
def song_detail(song_id):
    """Display details for a specific song"""
    song = Song.query.get(song_id)
    if not song:
        abort(404)
    # Legacy data has been migrated; no runtime migration required.

    return render_template('song_detail.html', song=song)


@search_bp.route('/file/<int:song_id>/<filename>', methods=['GET'])
def serve_file(song_id, filename):
    # Directory where score files are stored, set via environment variable
    directory = os.getenv('FILES_DIR')
    assert directory, "FILES_DIR environment variable is not set"
    """Serve score files safely"""
    song = Song.query.get(song_id)
    if not song:
        abort(404)

    # Check relational Score objects only (legacy data already migrated)
    file_found = any(
        getattr(score_obj, 'file', None) == filename
        for score_obj in getattr(song, 'scores', []) or []
    )

    if not file_found:
        abort(403)

    files_dir = directory
    file_path = os.path.join(files_dir, filename)

    file_path = os.path.abspath(file_path)
    files_dir = os.path.abspath(files_dir)

    if not file_path.startswith(files_dir):
        abort(403)

    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(files_dir, filename)
