"""
RAG service — Q&A answering with grounding contract.

Thin wrapper over the grounding module that services can import.
"""

import logging

from app.rag.grounding import ask_question as _grounded_ask

logger = logging.getLogger(__name__)


def ask(
    question: str,
    subject: str | None = None,
    chapter: str | None = None,
) -> dict:
    """
    Answer a student question using the grounded RAG pipeline.

    Returns a dict with keys: status, answer, missing, sources.
    """
    return _grounded_ask(question, subject, chapter)
