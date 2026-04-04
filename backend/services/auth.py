"""
Authentication service.

For now this uses mock tokens so protected routes can be tested
before full JWT integration is finished.
"""

from typing import Optional

TOKENS = {
    "prof-token": {"id": 1, "name": "Professor", "email": "prof@example.com"},
    "student-token": {"id": 2, "name": "Student", "email": "student@example.com"},
    "ta-token": {"id": 3, "name": "TA User", "email": "ta@example.com"},
}


def verify_token(token: str) -> Optional[dict]:
    """
    Return the user associated with a token if it is valid.
    """
    return TOKENS.get(token)