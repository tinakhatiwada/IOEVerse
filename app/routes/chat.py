"""
Chat routes — /chat.

Uses the grounded RAG service instead of raw Gemini calls.
"""

import logging
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    subject: Optional[str] = None
    chapter: Optional[str] = None


@router.post("/chat")
async def chat(body: ChatRequest):
    """
    Answer a student question using grounded RAG.

    Returns the grounding contract response with status, answer, missing, sources.
    """
    question = body.question.strip()
    if not question:
        return {"error": "Question is required"}

    try:
        result = rag_service.ask(
            question=question,
            subject=body.subject,
            chapter=body.chapter,
        )
        return result
    except Exception as e:
        logger.error("Chat error: %s", e)
        return {"error": str(e)}
