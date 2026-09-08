import json
import os
import time
import uuid

from flask import Blueprint, abort, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

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


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf'}


def is_allowed_image_filename(filename: str) -> bool:
    if not filename:
        return False
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_IMAGE_EXTENSIONS


@search_bp.route('/upload-score', methods=['POST'])
def upload_score():
    """Handle uploaded score image and attach it to a song.

    Expects multipart/form-data with fields:
      - title (required)
      - composer (required)
      - score_file (required) file upload (images only)
      - score_name (optional)
    """
    # basic form validation
    title = (request.form.get('title') or '').strip()
    composer = (request.form.get('composer') or '').strip()
    score_name = (request.form.get('score_name') or '').strip()

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if not composer:
        return jsonify({'error': 'Composer is required'}), 400

    if 'score_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['score_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    if not is_allowed_image_filename(filename):
        return jsonify({'error': 'Invalid file type'}), 400

    files_dir = os.getenv('FILES_DIR')
    if not files_dir:
        return jsonify({'error': 'Server not configured to store files'}), 500

    # ensure destination exists
    os.makedirs(files_dir, exist_ok=True)

    # avoid collisions: prefix with uuid
    unique_prefix = uuid.uuid4().hex
    safe_filename = f"{unique_prefix}_{filename}"
    dest_path = os.path.abspath(os.path.join(files_dir, safe_filename))
    files_dir_abs = os.path.abspath(files_dir)

    # ensure path stays inside files_dir
    if not dest_path.startswith(files_dir_abs):
        return jsonify({'error': 'Invalid file path'}), 400

    file.save(dest_path)

    # find or create song
    song = Song.query.filter_by(title=title).first()
    if not song:
        song = Song(title=title)
        db.session.add(song)
        db.session.flush()

    # add composer
    song.add_composer(composer)

    # add score record
    score_display_name = score_name or filename
    song.add_score({'name': score_display_name, 'file': safe_filename})

    db.session.commit()

    return jsonify({'message': 'Upload successful', 'song': song.get_metadata()}), 201


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
