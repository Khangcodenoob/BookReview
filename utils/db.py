"""Database utility functions."""
import sqlite3
from flask import g, current_app
from typing import Optional


def get_db() -> sqlite3.Connection:
    """Get database connection from Flask g object."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    """Close database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize database with schema."""
    with app.app_context():
        db = get_db()
        schema_file = app.config.get('SCHEMA_FILE', 'schema.sql')
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
        except FileNotFoundError:
            # Schema file not found, will be created by migration
            pass
        except Exception as e:
            app.logger.error(f"Error initializing database: {e}")
        finally:
            db.close()

