"""
Database connection management.

Provides a simple connection helper and schema initialisation.
Uses psycopg2 directly (no ORM) — matches the original app's approach.
"""

import logging
import os

import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection():
    """Return a new database connection with RealDictCursor."""
    return psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)


# ---------------------------------------------------------------------------
# Schema bootstrap
# ---------------------------------------------------------------------------

_SCHEMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))


def init_db():
    """Run schema.sql against the database (idempotent — uses IF NOT EXISTS)."""
    schema_path = os.path.join(_SCHEMA_DIR, "schema.sql")
    if not os.path.exists(schema_path):
        logger.warning("schema.sql not found at %s — skipping DB init", schema_path)
        return

    with open(schema_path, "r") as f:
        sql = f.read()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logger.info("Database schema initialised")
    except Exception:
        conn.rollback()
        logger.exception("Failed to initialise database schema")
        raise
    finally:
        conn.close()
