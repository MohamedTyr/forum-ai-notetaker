"""
Course member service layer.

Handles role/membership lookups and updates for course members.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def get_course_member(course_id: int, user_id: int) -> Optional[dict]:
    """
    Return one course member row for a given course and user.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM course_members WHERE course_id = ? AND user_id = ?",
            (course_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def update_course_member_role(course_id: int, user_id: int, role: str) -> bool:
    """
    Update a member role in a course.

    Returns True if a row was updated, otherwise False.
    """
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE course_members SET role = ?, updated_at = ? "
            "WHERE course_id = ? AND user_id = ?",
            (role, now, course_id, user_id),
        )
        conn.commit()
    return cursor.rowcount > 0
