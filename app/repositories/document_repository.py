"""
Document repository — database access for documents and document_chunks.

Used by both the ingestion pipeline (insert) and the RAG retriever (search).
"""

import logging
from typing import List

from app.database import get_connection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Writes (used by ingestion)
# ---------------------------------------------------------------------------

def insert_document(subject: str, chapter: str, source_filename: str) -> int:
    """Insert a document record and return its id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO documents (subject, chapter, source_filename)
                   VALUES (%s, %s, %s) RETURNING id""",
                (subject, chapter, source_filename),
            )
            doc_id = cur.fetchone()["id"]
        conn.commit()
        return doc_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def document_exists(source_filename: str) -> bool:
    """Check whether a document has already been ingested."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM documents WHERE source_filename = %s LIMIT 1",
                (source_filename,),
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def insert_chunks(chunks: List[dict]) -> int:
    """
    Batch-insert chunk rows.

    Each dict in *chunks* must have keys:
        document_id, subject, chapter, content, embedding, page

    Returns the number of rows inserted.
    """
    if not chunks:
        return 0

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            args = [
                (
                    c["document_id"],
                    c["subject"],
                    c["chapter"],
                    c["content"],
                    c["embedding"],      # list[float] — psycopg2 sends as array
                    c.get("page"),
                )
                for c in chunks
            ]
            cur.executemany(
                """INSERT INTO document_chunks
                       (document_id, subject, chapter, content, embedding, page)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                args,
            )
        conn.commit()
        return len(chunks)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Reads (used by retriever)
# ---------------------------------------------------------------------------

def search_similar(
    embedding: List[float],
    subject: str | None = None,
    chapter: str | None = None,
    k: int = 5,
) -> List[dict]:
    """
    Find the *k* most similar chunks using pgvector cosine distance.

    Optionally filter by subject and/or chapter at the SQL level.
    """
    conn = get_connection()
    try:
        conditions = []
        where_params: list = []

        if subject:
            conditions.append("subject = %s")
            where_params.append(subject)
        if chapter:
            conditions.append("chapter = %s")
            where_params.append(chapter)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        # Build params: embedding for cosine distance first, then WHERE params, then LIMIT
        embedding_str = str(embedding)

        query = f"""
            SELECT id, document_id, subject, chapter, content, page,
                   embedding <=> %s::vector AS distance
            FROM document_chunks
            {where}
            ORDER BY distance
            LIMIT %s
        """

        # Params order must match placeholder order in the query:
        # 1. %s::vector (cosine distance)
        # 2. WHERE %s values (if any)
        # 3. LIMIT %s
        params = [embedding_str] + where_params + [k]

        with conn.cursor() as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_documents(subject: str | None = None) -> List[dict]:
    """List ingested documents, optionally filtered by subject."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if subject:
                cur.execute(
                    "SELECT * FROM documents WHERE subject = %s ORDER BY uploaded_at DESC",
                    (subject,),
                )
            else:
                cur.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
