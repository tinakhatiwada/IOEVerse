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


@router.post("/auth/google-demo")
async def google_demo_login():
    """
    Demo Google login — creates a shared demo account and logs in.
    Real Google OAuth requires GCP credentials; this is a working placeholder.
    """
    try:
        # Try to sign up (will fail silently if already exists)
        try:
            signup("demo@google.ioeverse", "GoogleDemo2025!")
        except Exception:
            pass
        user = login("demo@google.ioeverse", "GoogleDemo2025!")
        return {"success": True, "message": "Signed in with Google", "user": user}
    except Exception as e:
        logger.error("Google demo login error: %s", e)
        return JSONResponse(
            {"success": False, "error": "Google sign-in unavailable. Please use email login."},
            status_code=503,
        )
