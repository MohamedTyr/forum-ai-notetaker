"""
Course routes.

Handles:
- create course
- join course
- list courses
- course details
- promote TA
- course sessions
"""

from flask import Blueprint, request, g

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from services.course_service import (
    create_course,
    get_courses_for_user,
    get_course_by_id,
    get_course_members,
    is_professor,
    is_course_member,
    join_course_by_invite_code,
    promote_member_to_ta,
)
from services.session_service import fetch_sessions_for_course

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/", methods=["POST"])
@auth_required
def create_new_course():
    """
    Create a course.
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()

    if not name:
        return error_response("Course name is required", 400)

    course = create_course(name, g.user)
    return success_response("Course created", course, 201)


@courses_bp.route("/", methods=["GET"])
@auth_required
def list_my_courses():
    """
    Get all courses for current user.
    """
    courses = get_courses_for_user(g.user["id"])
    return success_response("Courses retrieved", courses)


@courses_bp.route("/join", methods=["POST"])
@auth_required
def join_course():
    """
    Join course using invite code.
    """
    data = request.get_json(silent=True) or {}
    invite_code = data.get("invite_code", "").strip().upper()

    if not invite_code:
        return error_response("Invite code required", 400)

    membership = join_course_by_invite_code(invite_code, g.user)

    if not membership:
        return error_response("Invalid invite code", 404)

    return success_response("Joined course", membership, 201)


@courses_bp.route("/<int:course_id>", methods=["GET"])
@auth_required
def get_course_details(course_id: int):
    """
    Get course info + members.
    Invite code only visible to professor.
    """
    course = get_course_by_id(course_id)

    if not course:
        return error_response("Course not found", 404)

    if not is_course_member(course_id, g.user["id"]):
        return error_response("Access denied", 403)

    data = {
        "id": course["id"],
        "name": course["name"],
        "members": get_course_members(course_id),
    }

    if is_professor(course_id, g.user["id"]):
        data["invite_code"] = course["invite_code"]

    return success_response("Course retrieved", data)


@courses_bp.route("/<int:course_id>/sessions", methods=["GET"])
@auth_required
def list_course_sessions(course_id: int):
    """
    Get sessions for a course.
    """
    if not is_course_member(course_id, g.user["id"]):
        return error_response("Access denied", 403)

    sessions = fetch_sessions_for_course(course_id)
    return success_response("Sessions retrieved", sessions)


@courses_bp.route("/<int:course_id>/promote-ta", methods=["POST"])
@auth_required
def promote_to_ta(course_id: int):
    """
    Promote a student to TA (professor only).
    """
    if not is_professor(course_id, g.user["id"]):
        return error_response("Only professor can promote", 403)

    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if user_id is None:
        return error_response("user_id required", 400)

    try:
        user_id = int(user_id)
    except ValueError:
        return error_response("user_id must be int", 400)

    membership = promote_member_to_ta(course_id, user_id)

    if not membership:
        return error_response("User not in course", 404)

    return success_response("Promoted to TA", membership)