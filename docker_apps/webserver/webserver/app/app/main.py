"""Main Flask app module (legacy - use run.py instead)"""
import sys
from pathlib import Path

# Add parent directory to path to allow importing app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
