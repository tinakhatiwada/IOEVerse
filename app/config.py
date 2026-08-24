"""
Application configuration — loads from environment and validates.

Every required setting lives here.  Import `settings` anywhere you need
config values instead of reading os.environ directly.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    """Return an env var or raise with a helpful message."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set.  Copy .env.example → .env and fill it in, "
            "or set it in your deploy environment."
        )
    return value


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    SECRET_KEY: str
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIM: int = 3072
    LLM_MODEL: str = "models/gemini-3.6-flash"
    LLM_TEMPERATURE: float = 0.8
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_K: int = 5


settings = Settings(
    DATABASE_URL=_require("DATABASE_URL"),
    GOOGLE_API_KEY=_require("GOOGLE_API_KEY"),
    SECRET_KEY=_require("FLASK_SECRET_KEY"),  # env var name kept for backwards compat
)

# langchain_google_genai reads this env var directly
os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
