"""
Authentication middleware.

This decorator protects routes that require a logged-in user.
It reads the bearer token from the Authorization header,
verifies it, and stores the current user in Flask's request context.
"""

from functools import wraps
from flask import request, g

from utils.responses import error_response
from services.auth_service import verify_token


def auth_required(route_function):
    """
    Protect a route so only authenticated users can access it.
    """
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header:
            return error_response("Missing Authorization header", 401)

        if not auth_header.startswith("Bearer "):
            return error_response("Invalid Authorization header format", 401)

        token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return error_response("Missing token", 401)

        user = verify_token(token)

        if not user:
            return error_response("Invalid or expired token", 401)

        g.user = user
        return route_function(*args, **kwargs)

    return wrapper