#!/usr/bin/env python3
"""
Initialize PR Test database tables.

Creates all tables defined in backend/database.py if they don't exist.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import Base, engine, DB_PATH, PRTestRun, PRTestMetrics

def init_db():
    """Initialize database tables."""
    print(f" Database path: {DB_PATH}")
    print(f" Creating database tables...")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print(f" Database tables created successfully!")
    print(f"\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_db()
