#!/usr/bin/env python
"""Database management CLI"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models.song import Song
import json

def reset_db():
    """Reset the database"""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset successfully")

def list_songs():
    """List all songs in the database"""
    app = create_app()
    with app.app_context():
        songs = Song.query.all()
        if not songs:
            print("No songs found")
            return

        print(f"\n📀 Total songs: {len(songs)}\n")
        for song in songs:
            print(f"  • {song.title}")
            print(f"    ID: {song.id}")
            print(f"    Genre: {song.genre.name if song.genre else 'n/d'}")
            print(f"    Subgenre: {song.subgenre.name if song.subgenre else 'n/d'}")
            print(f"    Interpreters: {', '.join([i.name for i in song.interpreters]) if song.interpreters else 'n/d'}")
            print(f"    Composers: {', '.join([c.name for c in song.composers]) if song.composers else 'n/d'}")
            print(f"    Scores: {', '.join([s.file for s in song.scores]) if song.scores else 'n/d'}")
            print()

def seed():
    """Seed the database with sample data"""
    from seed_db import seed_database
    seed_database()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python db_cli.py [reset|list|seed]")
        print("\nCommands:")
        print("  reset   - Reset the database")
        print("  list    - List all songs")
        print("  seed    - Seed with sample data")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'reset':
        reset_db()
    elif command == 'list':
        list_songs()
    elif command == 'seed':
        seed()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
