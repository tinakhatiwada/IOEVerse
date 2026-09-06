"""Database connection and schema bootstrap for IOEverse."""

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

# Core tables that must always exist (no pgvector dependency)
_CORE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    subject TEXT NOT NULL,
    chapter TEXT NOT NULL,
    source_filename TEXT UNIQUE,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);
"""

# pgvector-dependent tables (only created if extension is available)
_VECTOR_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    chapter TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    page INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_subject_chapter
    ON document_chunks(subject, chapter);
"""


def _run_sql(conn, sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def init_db():
    """Bootstrap DB schema: core tables first, then pgvector tables."""
    # Phase 1: users + documents (no pgvector needed)
    try:
        conn = get_connection()
    except Exception:
        logger.exception("Cannot connect to database — skipping schema init")
        return

    try:
        _run_sql(conn, _CORE_SCHEMA)
        logger.info("Core schema (users, documents) ready")
    except Exception:
        conn.rollback()
        logger.exception("Failed to create core schema")
    finally:
        conn.close()

    # Phase 2: pgvector + chunks (optional — RAG won't work without it,
    # but auth and basic navigation will)
    try:
        conn2 = get_connection()
        _run_sql(conn2, _VECTOR_SCHEMA)
        logger.info("Vector schema (pgvector, document_chunks) ready")
        conn2.close()
    except Exception:
        logger.warning(
            "pgvector schema init failed — RAG/quiz features may be limited. "
            "Run: CREATE EXTENSION IF NOT EXISTS vector; in your Postgres DB."
        )
