"""
Domain models for the quiz system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    difficulty: str
    topic: str
    chapter: str


@dataclass
class QuizSession:
    session_id: str
    questions: List[QuizQuestion]
    subject: str
    chapter: str
    current_question: int = 0
    score: int = 0
    completed: bool = False
    answers: List[int] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
