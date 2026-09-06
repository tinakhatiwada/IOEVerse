"""
Grounding logic — enforces the grounding contracts for Q&A and quiz.

Combines retrieval + LLM call + JSON parsing into a single function
per contract.  No Flask knowledge.
"""

import json
import logging
import re
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.rag.prompts import QA_GROUNDING_TEMPLATE, QUIZ_GROUNDING_TEMPLATE, QUIZ_FALLBACK_TEMPLATE
from app.rag.retriever import retrieve_context_string

logger = logging.getLogger(__name__)

_llm = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            # gemini-3.6-flash uses fixed sampling; temperature param is ignored
        )
    return _llm


def _extract_text(response) -> str:
    """
    Extract plain text from a LangChain / Gemini response.

    Newer Gemini models return response.content as a list of content blocks:
      [{'type': 'text', 'text': '...', 'extras': {...}}]
    Older behaviour was a plain string.
    """
    content = response.content if hasattr(response, "content") else response
    if isinstance(content, list):
        # Extract the 'text' field from each text-type block
        parts = [block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text"]
        return "\n".join(parts)
    return str(content)


def _extract_json(text: str) -> dict | None:
    """Best-effort extraction of a JSON object from LLM output."""
    # Try the whole string first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Strip markdown code fences if present
    stripped = re.sub(r"^```[a-z]*\n?", "", text.strip(), flags=re.MULTILINE)
    stripped = re.sub(r"```$", "", stripped.strip())
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    # Fall back to regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


# ---------------------------------------------------------------------------
# Q&A contract
# ---------------------------------------------------------------------------

def ask_question(
    question: str,
    subject: str | None = None,
    chapter: str | None = None,
) -> dict[str, Any]:
    """
    Answer a student question using the grounding contract.

    Returns a dict matching one of:
      {"status": "grounded",   "answer": "...", "missing": null,  "sources": [...]}
      {"status": "partial",    "answer": "...", "missing": "...", "sources": [...]}
      {"status": "not_found",  "answer": null,  "missing": "...", "sources": []}
    """
    context = retrieve_context_string(question, subject, chapter)

    if not context:
        return {
            "status": "not_found",
            "answer": None,
            "missing": "No documents have been ingested for this subject/chapter yet.",
            "sources": [],
        }

    chain = QA_GROUNDING_TEMPLATE | _get_llm()
    response = chain.invoke({"context": context, "question": question})
    response_text = _extract_text(response)

    parsed = _extract_json(response_text)
    if parsed and "status" in parsed:
        return parsed

    # Fallback: model didn't follow the contract — wrap raw answer as partial
    logger.warning("LLM did not return grounding JSON, wrapping as partial")
    return {
        "status": "partial",
        "answer": response_text,
        "missing": "Could not verify grounding status — treat this answer with caution.",
        "sources": [],
    }


# ---------------------------------------------------------------------------
# Quiz contract
# ---------------------------------------------------------------------------

def generate_grounded_question(
    subject: str,
    chapter: str,
    difficulty: str = "Beginner",
) -> dict[str, Any]:
    """
    Generate a single quiz question using the grounding contract.

    Returns a dict matching one of:
      {"sufficient": true, "status": "grounded", "question": "...", ...}
      {"sufficient": false, "status": "insufficient_context", ...}
    """
    query = f"{chapter} concepts fundamentals"
    context = retrieve_context_string(query, subject, chapter)

    if not context:
        return {
            "sufficient": False,
            "status": "insufficient_context",
            "question": None,
            "message": "No documents have been ingested for this subject/chapter.",
        }

    chain = QUIZ_GROUNDING_TEMPLATE | _get_llm()
    response = chain.invoke({
        "context": context,
        "subject": subject,
        "chapter": chapter,
        "difficulty": difficulty,
    })
    response_text = _extract_text(response)

    parsed = _extract_json(response_text)
    if parsed and "status" in parsed:
        return parsed

    logger.warning("LLM did not return quiz grounding JSON")
    return {
        "sufficient": False,
        "status": "insufficient_context",
        "question": None,
        "message": "Model did not return a structured response.",
    }


# ---------------------------------------------------------------------------
# Fallback quiz — no documents needed
# ---------------------------------------------------------------------------

def generate_fallback_question(
    subject: str,
    chapter: str,
    difficulty: str = "Beginner",
) -> dict[str, Any]:
    """
    Generate a quiz question directly from LLM knowledge (no RAG context).
    Used when no documents have been ingested for a subject/chapter.
    """
    try:
        chain = QUIZ_FALLBACK_TEMPLATE | _get_llm()
        response = chain.invoke({
            "subject": subject,
            "chapter": chapter,
            "difficulty": difficulty,
        })
        response_text = _extract_text(response)
        parsed = _extract_json(response_text)
        if parsed and parsed.get("question") and parsed.get("options"):
            return parsed
        logger.warning("Fallback LLM did not return valid quiz JSON")
    except Exception as e:
        logger.error("Fallback question generation error: %s", e)
    return {"question": None}
