"""Run once to create all database tables."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import create_tables

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Done.")
