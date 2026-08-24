"""
Retriever — fetches relevant document chunks for a query.

This module talks to the document_repository (pgvector) and returns
context strings.  It has no knowledge of Flask, routes, or services.
"""

import logging
from typing import List

from app.rag.embeddings import embed_text
from app.repositories import document_repository

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    subject: str | None = None,
    chapter: str | None = None,
    k: int = 5,
) -> List[dict]:
    """
    Embed *query* and return the top-k similar chunks from pgvector.

    Each returned dict has keys: id, document_id, subject, chapter,
    content, page, distance.
    """
    try:
        embedding = embed_text(query)
        results = document_repository.search_similar(
            embedding=embedding,
            subject=subject,
            chapter=chapter,
            k=k,
        )
        return results
    except Exception as e:
        logger.error("Retrieval failed: %s", e)
        return []


def retrieve_context_string(
    query: str,
    subject: str | None = None,
    chapter: str | None = None,
    k: int = 5,
) -> str:
    """Convenience: retrieve chunks and join their content into a single string."""
    chunks = retrieve(query, subject, chapter, k)
    if not chunks:
        return ""
    return "\n\n".join(c["content"] for c in chunks)
