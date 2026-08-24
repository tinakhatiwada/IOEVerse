"""
User repository — all database access for the users table.
"""

import logging

from app.database import get_connection

logger = logging.getLogger(__name__)


def find_by_email(email: str) -> dict | None:
    """Look up a user by email.  Returns a dict or None."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cur.fetchone()
    finally:
        conn.close()


def create(email: str, password_hash: str) -> dict:
    """Insert a new user and return the created row."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING *",
                (email, password_hash),
            )
            user = cur.fetchone()
        conn.commit()
        return user
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
