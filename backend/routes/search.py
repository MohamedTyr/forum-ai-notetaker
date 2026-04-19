"""
Search routes.

These routes expose search across session titles, transcript content,
and AI-generated notes.

Search results are restricted to sessions belonging to courses the
authenticated user is a member of, so search follows the same
access-control model as the rest of the application.
"""

from flask import Blueprint, g, request

from middleware.auth import auth_required
from services.search_service import search
from utils.responses import error_response, success_response

search_bp = Blueprint("search", __name__)


@search_bp.route("/", methods=["GET"])
@auth_required
def search_sessions():
    """
    Search sessions by title, transcript content, and notes.

    The query is provided through the `q` query parameter. Results are
    filtered to sessions visible to the authenticated user.

    Query Parameters:
        q: The search string to match against session titles,
           transcript content, and generated notes.

    Returns:
        A 400 error if `q` is missing, empty, or too long.
        A 200 success response containing a list of matching sessions,
        which may be empty if no matches are found.

    Example:
        GET /api/search?q=memory+management
    """
    query = request.args.get("q", "").strip()

    if not query:
        return error_response("Search query parameter 'q' is required", 400)

    try:
        results = search(query, g.user["id"])
    except ValueError as exc:
        return error_response(str(exc), 400)

    return success_response("Search completed", results)