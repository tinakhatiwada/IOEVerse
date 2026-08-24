"""
Page routes — serve HTML templates.

No logic, just template renders.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app import templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/engineering", response_class=HTMLResponse)
async def engineering(request: Request):
    return templates.TemplateResponse(request, "engineering.html")


@router.get("/semester", response_class=HTMLResponse)
async def semester(request: Request):
    return templates.TemplateResponse(request, "semester.html")


@router.get("/subject", response_class=HTMLResponse)
async def subject(request: Request):
    return templates.TemplateResponse(request, "subject.html")


@router.get("/physics", response_class=HTMLResponse)
async def physics(request: Request):
    return templates.TemplateResponse(request, "physics.html")


@router.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request):
    return templates.TemplateResponse(request, "quiz.html")
