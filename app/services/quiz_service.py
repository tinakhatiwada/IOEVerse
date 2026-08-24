"""
Quiz service — quiz generation, session management, and answer submission.

`active_sessions` lives here in process memory.
Known limitation: a restart or second instance loses/splits state.
Move to Postgres or Redis once past prototype stage.
"""

import logging
import uuid
from typing import List

from app.models.quiz import QuizQuestion, QuizSession
from app.rag.grounding import generate_grounded_question

logger = logging.getLogger(__name__)

# In-memory session store (single-instance only)
active_sessions: dict[str, QuizSession] = {}

# ---------------------------------------------------------------------------
# Chapter structure — static curriculum data
# ---------------------------------------------------------------------------

CHAPTER_STRUCTURE: dict[str, list[str]] = {
    "Programming in C": [
        "Introduction to Programming",
        "Basic Structure of C Program",
        "Variables and Data Types",
        "Operators and Expressions",
        "Control Structures",
        "Functions and Recursion",
        "Arrays and Strings",
        "Pointers and Memory Management",
        "Structures and Unions",
        "File Operations",
    ],
    "Engineering Mathematics I": [
        "Complex Numbers",
        "Matrices and Determinants",
        "System of Linear Equations",
        "Sequences and Series",
        "Limits and Continuity",
        "Differentiation",
        "Applications of Derivatives",
        "Integration Techniques",
    ],
    "Engineering Physics": [
        "Mechanics and Motion",
        "Work, Energy and Power",
        "Oscillations and Waves",
        "Thermodynamics",
        "Optics and Light",
        "Modern Physics",
        "Atomic Structure",
        "Quantum Mechanics Basics",
    ],
    "Digital Logic": [
        "Number Systems",
        "Boolean Algebra",
        "Logic Gates",
        "Combinational Circuits",
        "Karnaugh Maps",
        "Sequential Circuits",
        "Flip-Flops and Latches",
        "Counters and Registers",
        "Memory Systems",
    ],
    "Basic Electrical Engineering": [
        "Circuit Fundamentals",
        "Ohm's Law and Kirchhoff's Laws",
        "Network Theorems",
        "AC Circuit Analysis",
        "Three-Phase Systems",
        "Magnetic Circuits",
        "Transformers",
        "Electrical Machines",
        "Measurement and Instrumentation",
    ],
    "Engineering Drawing I": [
        "Drawing Instruments and Materials",
        "Lettering and Dimensioning",
        "Geometric Constructions",
        "Orthographic Projections",
        "Isometric Drawings",
        "Sectional Views",
        "Auxiliary Views",
        "Development of Surfaces",
    ],
}


def get_subjects() -> list[str]:
    return list(CHAPTER_STRUCTURE.keys())


def get_chapters(subject: str) -> list[str]:
    return CHAPTER_STRUCTURE.get(subject, [])


import asyncio

def _generate_one_question(subject: str, chapter: str, difficulty: str, index: int, total: int) -> QuizQuestion | None:
    """Generate a single grounded question. Returns None if not sufficient."""
    try:
        result = generate_grounded_question(subject, chapter, difficulty)
        if result.get("sufficient") and result.get("status") == "grounded":
            logger.info("Generated question %d/%d for %s", index + 1, total, chapter)
            return QuizQuestion(
                question=result["question"],
                options=result["options"],
                correct_answer=result["correct_answer"],
                explanation=result.get("explanation", ""),
                difficulty=difficulty,
                topic=subject,
                chapter=chapter,
            )
        else:
            logger.warning(
                "Skipped question %d/%d — insufficient context: %s",
                index + 1, total, result.get("message", ""),
            )
    except Exception as e:
        logger.error("Error generating question %d: %s", index + 1, e)
    return None


def generate_quiz(
    subject: str,
    chapter: str,
    num_questions: int = 5,
    difficulty: str = "Beginner",
) -> QuizSession:
    """
    Generate a quiz and return a new QuizSession.

    All questions are generated in parallel using a thread pool so the
    total wait time is ~1× latency instead of N× latency.
    """
    with __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]).ThreadPoolExecutor(max_workers=num_questions) as pool:
        futures = [
            pool.submit(_generate_one_question, subject, chapter, difficulty, i, num_questions)
            for i in range(num_questions)
        ]
        results = [f.result() for f in futures]

    questions = [q for q in results if q is not None]

    session_id = str(uuid.uuid4())
    session = QuizSession(
        session_id=session_id,
        questions=questions,
        subject=subject,
        chapter=chapter,
    )
    active_sessions[session_id] = session
    return session



# ---------------------------------------------------------------------------
# Answer submission
# ---------------------------------------------------------------------------

def submit_answer(session_id: str, user_answer: int) -> dict:
    """
    Submit an answer for the current question.

    Returns a response dict with correctness info and either the next
    question or final results.
    Raises KeyError if the session is not found.
    """
    if session_id not in active_sessions:
        raise KeyError("Session not found")

    session = active_sessions[session_id]
    current_q = session.questions[session.current_question]

    is_correct = user_answer == current_q.correct_answer
    if is_correct:
        session.score += 1

    session.answers.append(user_answer)

    response = {
        "success": True,
        "is_correct": is_correct,
        "correct_answer": current_q.correct_answer,
        "explanation": current_q.explanation,
        "current_score": session.score,
        "question_number": session.current_question + 1,
        "total_questions": len(session.questions),
    }

    session.current_question += 1

    if session.current_question >= len(session.questions):
        session.completed = True
        response["quiz_completed"] = True
        response["final_score"] = session.score
        response["percentage"] = (
            (session.score / len(session.questions)) * 100
            if session.questions
            else 0
        )
    else:
        next_q = session.questions[session.current_question]
        response["next_question"] = {
            "question": next_q.question,
            "options": next_q.options,
            "topic": next_q.topic,
            "difficulty": next_q.difficulty,
        }

    return response


def get_session(session_id: str) -> QuizSession | None:
    return active_sessions.get(session_id)
