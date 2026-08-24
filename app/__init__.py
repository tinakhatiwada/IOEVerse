"""
IOEVERSE application factory.

Creates and configures the FastAPI app, includes routers, mounts
static files, and runs one-time initialisation (database schema).
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resolve paths relative to the project root (one level up from app/)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Shared Jinja2 templates instance — routes import this
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def create_app() -> FastAPI:
    """Application factory — returns a configured FastAPI instance."""

    app = FastAPI(
        title="IOEVERSE",
        description="RAG-powered study assistant for IOE 1st semester",
        version="2.0.0",
    )

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Static files
    # ------------------------------------------------------------------
    if os.path.isdir(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # ------------------------------------------------------------------
    # Include routers
    # ------------------------------------------------------------------
    from app.routes.auth import router as auth_router
    from app.routes.chat import router as chat_router
    from app.routes.pages import router as pages_router
    from app.routes.quiz import router as quiz_router

    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(quiz_router)
    app.include_router(pages_router)

    # ------------------------------------------------------------------
    # Database initialisation (idempotent)
    # ------------------------------------------------------------------
    from app.database import init_db

    @app.on_event("startup")
    async def startup():
        try:
            init_db()
        except Exception:
            logger.warning(
                "Database schema init failed — this is expected if pgvector "
                "is not yet enabled or schema.sql doesn't exist yet."
            )
        logger.info("IOEVERSE app started")

    return app
