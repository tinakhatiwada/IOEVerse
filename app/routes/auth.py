"""
Auth routes — /login, /signup.

Thin HTTP wrappers: parse request → call service → return response.
"""

import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app import templates
from app.services.auth_service import AuthError, login, signup

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


# ---------------------------------------------------------------------------
# Pydantic models for request validation
# ---------------------------------------------------------------------------

class AuthRequest(BaseModel):
    email: str
    password: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")


@router.post("/signup")
async def signup_route(body: AuthRequest):
    try:
        user = signup(body.email, body.password)
        return JSONResponse(
            {"success": True, "message": "User registered successfully"},
            status_code=201,
        )
    except AuthError as e:
        return JSONResponse(
            {"success": False, "error": e.message},
            status_code=e.status_code,
        )
    except Exception as e:
        logger.error("Error in signup: %s", e)
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500,
        )


@router.post("/login")
async def login_route(body: AuthRequest):
    try:
        user = login(body.email, body.password)
        return {"success": True, "message": "Login successful", "user": user}
    except AuthError as e:
        return JSONResponse(
            {"success": False, "error": e.message},
            status_code=e.status_code,
        )


@router.post("/google-demo")
async def google_demo_login():
    """
    Demo Google login — works even if the database isn't fully set up yet.
    Creates a guest session the frontend can use to navigate the app.
    """
    # Try proper DB-backed login first
    try:
        try:
            signup("demo@google.ioeverse", "GoogleDemo2025!")
        except Exception:
            pass  # User already exists — fine
        user = login("demo@google.ioeverse", "GoogleDemo2025!")
        return {"success": True, "message": "Signed in with Google", "user": user}
    except Exception as e:
        logger.warning("DB-backed Google login failed (%s) — using guest session", e)

    # Fallback: return a guest token so frontend can proceed
    return {
        "success": True,
        "message": "Signed in as guest",
        "user": {"id": 0, "email": "guest@ioeverse"},
        "guest": True,
    }
