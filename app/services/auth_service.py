"""
Auth service — signup and login business logic.

Sits between routes (HTTP) and repositories (DB).  Contains the
password hashing / verification logic.
"""

import logging

from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories import user_repository

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Raised for authentication/signup failures."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def signup(email: str, password: str) -> dict:
    """
    Register a new user.

    Returns the created user dict (without password_hash).
    Raises AuthError if validation fails or user already exists.
    """
    if not email or not password:
        raise AuthError("Email and password are required", 400)

    existing = user_repository.find_by_email(email)
    if existing:
        raise AuthError("User already exists", 409)

    hashed = generate_password_hash(password)
    user = user_repository.create(email, hashed)

    # Strip the hash before returning
    safe_user = dict(user)
    safe_user.pop("password_hash", None)
    return safe_user


def login(email: str, password: str) -> dict:
    """
    Authenticate a user.

    Returns the user dict (without password_hash).
    Raises AuthError on failure — uses a generic message so we don't
    reveal whether the email exists.
    """
    if not email or not password:
        raise AuthError("Email and password required", 400)

    user = user_repository.find_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        raise AuthError("Invalid email or password", 401)

    safe_user = dict(user)
    safe_user.pop("password_hash", None)
    return safe_user
