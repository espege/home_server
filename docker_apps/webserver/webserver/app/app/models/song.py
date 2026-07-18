from app import db


song_composers = db.Table(
    'song_composers',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('composer_id', db.Integer, db.ForeignKey('composers.id'), primary_key=True),
)

song_interpreters = db.Table(
    'song_interpreters',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('interpreter_id', db.Integer, db.ForeignKey('interpreters.id'), primary_key=True),
)

song_scores = db.Table(
    'song_scores',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('score_id', db.Integer, db.ForeignKey('scores.id'), primary_key=True),
)

song_media_links = db.Table(
    'song_media_links',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('media_link_id', db.Integer, db.ForeignKey('media_links.id'), primary_key=True),
)


class Composer(db.Model):
    __tablename__ = 'composers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    songs = db.relationship('Song', secondary=song_composers, back_populates='composers')

    @property
    def name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Interpreter(db.Model):
    __tablename__ = 'interpreters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    songs = db.relationship('Song', secondary=song_interpreters, back_populates='interpreters')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    file = db.Column(db.String(255), nullable=False, unique=True)
    songs = db.relationship('Song', secondary=song_scores, back_populates='scores')

    def __repr__(self):
        return self.file

    def __str__(self):
        return self.file


class MediaLink(db.Model):
    __tablename__ = 'media_links'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000), nullable=False, unique=True)
    songs = db.relationship('Song', secondary=song_media_links, back_populates='media_links')

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.url

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    songs = db.relationship('Song', back_populates='genre')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class SubGenre(db.Model):
    __tablename__ = 'subgenres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    songs = db.relationship('Song', back_populates='subgenre')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    subgenre_id = db.Column(db.Integer, db.ForeignKey('subgenres.id'), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=True)
    # Legacy columns have been migrated; they are intentionally removed from
    # the model to keep the codebase clean. The database may still contain
    # those physical columns for backward compatibility, but the ORM no
    # longer maps them.
    created_at = db.Column(db.DateTime, default=db.func.now())

    genre = db.relationship('Genre', back_populates='songs')
    subgenre = db.relationship('SubGenre', back_populates='songs')
    composers = db.relationship('Composer', secondary=song_composers, back_populates='songs')
    interpreters = db.relationship('Interpreter', secondary=song_interpreters, back_populates='songs')
    scores = db.relationship('Score', secondary=song_scores, back_populates='songs')
    media_links = db.relationship('MediaLink', secondary=song_media_links, back_populates='songs')

    def __repr__(self):
        return f'<Song {self.title}>'

    def __str__(self):
        return self.title

    def add_genre(self, genre_name):
        genre_name = genre_name.strip()
        if not genre_name:
            return None

        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)

        self.genre = genre
        return genre

    def add_subgenre(self, subgenre_name):
        subgenre_name = subgenre_name.strip()
        if not subgenre_name:
            return None

        subgenre = SubGenre.query.filter_by(name=subgenre_name).first()
        if not subgenre:
            subgenre = SubGenre(name=subgenre_name)
            db.session.add(subgenre)

        self.subgenre = subgenre
        return subgenre

    def add_score(self, score):
        """Add a score. Accepts a dict with name/file or a string."""
        if isinstance(score, str):
            score_data = {'name': score, 'file': score}
        elif isinstance(score, dict):
            score_data = {'name': score.get('name', ''), 'file': score.get('file', '')}
        else:
            raise TypeError("Score must be a string or dict with 'name'/'file' keys")

        if not score_data['name'] or not score_data['file']:
            return None

        score_obj = Score.query.filter_by(file=score_data['file']).first()
        if not score_obj:
            score_obj = Score(name=score_data['name'], file=score_data['file'])
            db.session.add(score_obj)

        if score_obj not in self.scores:
            self.scores.append(score_obj)

        return score_obj

    def add_composer(self, composer_name):
        composer_name = composer_name.strip()
        if not composer_name:
            return None

        parts = composer_name.split()
        first_name = parts[0]
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else None

        composer = None
        if last_name:
            composer = Composer.query.filter_by(first_name=first_name, last_name=last_name).first()
        else:
            composer = Composer.query.filter_by(first_name=first_name, last_name=None).first()

        if not composer:
            composer = Composer(first_name=first_name, last_name=last_name)
            db.session.add(composer)

        if composer not in self.composers:
            self.composers.append(composer)

        return composer

    def add_interpreter(self, interpreter_name):
        interpreter_name = interpreter_name.strip()
        if not interpreter_name:
            return None

        interpreter = Interpreter.query.filter_by(name=interpreter_name).first()
        if not interpreter:
            interpreter = Interpreter(name=interpreter_name)
            db.session.add(interpreter)

        if interpreter not in self.interpreters:
            self.interpreters.append(interpreter)

        return interpreter

    def add_media_link(self, media_link_url):
        media_link_url = media_link_url.strip()
        if not media_link_url:
            return None

        media_link = MediaLink.query.filter_by(url=media_link_url).first()
        if not media_link:
            media_link = MediaLink(url=media_link_url)
            db.session.add(media_link)

        if media_link not in self.media_links:
            self.media_links.append(media_link)

        return media_link

    # Legacy migration is complete and handled by a one-time migration script.
    # No runtime legacy handling remains in the model.

    def get_metadata(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre.name if self.genre else None,
            'subgenre': self.subgenre.name if self.subgenre else None,
            'scores': [
                {'id': score.id, 'name': score.name, 'file': score.file}
                for score in self.scores
            ],
            'interpreters': [interpreter.name for interpreter in self.interpreters],
            'composers': [composer.name for composer in self.composers],
            'media_links': [media_link.url for media_link in self.media_links],
        }
