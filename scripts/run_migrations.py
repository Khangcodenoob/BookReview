"""
Script to run database migrations.
Run this to add indexes and other database improvements.
"""
import sqlite3
import os
from pathlib import Path

# Get the project root directory (parent of scripts folder)
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "books.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"


def run_migration(migration_file: Path):
    """Run a single migration file."""
    print(f"Running migration: {migration_file.name}")
    try:
        conn = sqlite3.connect(DB_PATH)
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for statement in statements:
            try:
                conn.execute(statement)
            except sqlite3.OperationalError as e:
                # Ignore "already exists" errors for indexes
                if "already exists" not in str(e).lower():
                    print(f"  Warning: {e}")
        
        conn.commit()
        conn.close()
        print(f"  Migration {migration_file.name} completed")
        return True
    except Exception as e:
        print(f"  Error running {migration_file.name}: {e}")
        return False


def main():
    """Run all pending migrations."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Creating database...")
        # Database will be created by app on first run
        return
    
    if not MIGRATIONS_DIR.exists():
        print(f"Migrations directory not found at {MIGRATIONS_DIR}")
        return
    
    print(f"Running migrations for database: {DB_PATH}")
    print("-" * 50)
    
    # Get all SQL files in migrations directory
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    if not migration_files:
        print("No migration files found")
        return
    
    success_count = 0
    for migration_file in migration_files:
        if run_migration(migration_file):
            success_count += 1
    
    print("-" * 50)
    print(f"Completed: {success_count}/{len(migration_files)} migrations")


if __name__ == "__main__":
    main()
