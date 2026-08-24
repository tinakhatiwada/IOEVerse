"""
Quiz routes — generate quizzes, submit answers, get history.

All business logic lives in quiz_service; routes just translate
HTTP ↔ service calls.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services import quiz_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["quiz"])


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class GenerateQuizRequest(BaseModel):
    subject: str
    chapter: str
    difficulty: str = "Beginner"
    num_questions: int = 5


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/subjects")
async def get_subjects():
    return {"subjects": quiz_service.get_subjects()}


@router.get("/chapters")
async def get_chapters(subject: str = Query(..., description="Subject name")):
    chapters = quiz_service.get_chapters(subject)
    return {"success": True, "chapters": chapters}


@router.get("/topics")
async def get_topics():
    """Alias for subjects (backwards compat with existing frontend)."""
    return {"topics": quiz_service.get_subjects()}


@router.get("/difficulties")
async def get_difficulties():
    return {"difficulties": ["Beginner", "Intermediate", "Advanced"]}


@router.post("/generate-quiz")
async def generate_quiz(body: GenerateQuizRequest):
    try:
        if body.subject not in quiz_service.get_subjects():
            return {"success": False, "error": "Invalid subject"}

        if body.chapter not in quiz_service.get_chapters(body.subject):
            return {"success": False, "error": "Invalid chapter for the selected subject"}

        session = quiz_service.generate_quiz(
            body.subject, body.chapter, body.num_questions, body.difficulty
        )

        if not session.questions:
            return {
                "success": False,
                "error": "Could not generate any grounded questions for this chapter. "
                         "Ensure documents have been ingested for this subject.",
            }

        first_q = session.questions[0]
        return {
            "success": True,
            "session_id": session.session_id,
            "subject": body.subject,
            "chapter": body.chapter,
            "total_questions": len(session.questions),
            "current_question": 0,
            "question_data": {
                "question": first_q.question,
                "options": first_q.options,
                "topic": first_q.topic,
                "chapter": first_q.chapter,
                "difficulty": first_q.difficulty,
            },
        }

    except Exception as e:
        logger.error("Error generating quiz: %s", e)
        return {"success": False, "error": str(e)}


@router.post("/submit-answer")
async def submit_answer(body: SubmitAnswerRequest):
    try:
        result = quiz_service.submit_answer(body.session_id, body.answer)
        return result
    except KeyError:
        return {"success": False, "error": "Session not found"}
    except Exception as e:
        logger.error("Error submitting answer: %s", e)
        return {"success": False, "error": str(e)}


@router.get("/get-quiz-history")
async def get_quiz_history(session_id: str = Query(...)):
    try:
        session = quiz_service.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        results = []
        for i, question in enumerate(session.questions[: len(session.answers)]):
            user_answer = session.answers[i]
            results.append({
                "question_number": i + 1,
                "question": question.question,
                "options": question.options,
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": user_answer == question.correct_answer,
                "explanation": question.explanation,
                "topic": question.topic,
                "difficulty": question.difficulty,
            })

        return {
            "success": True,
            "session_id": session_id,
            "total_questions": len(session.questions),
            "completed_questions": len(session.answers),
            "score": session.score,
            "results": results,
        }

    except Exception as e:
        logger.error("Error getting quiz history: %s", e)
        return {"success": False, "error": str(e)}
