def search_sessions_for_user(user_id: int, query: str) -> list[dict]:
    """
    Search sessions by title, transcript content, and generated notes,
    restricted to the authenticated user's courses.

    A session is included in the results if:
    - the user belongs to the session's course, and
    - the query matches at least one of:
        • session title
        • transcript content
        • notes summary
        • notes topics (stored as JSON string)
        • notes action items (stored as JSON string)

    In addition to the session fields, this query also returns the
    matching transcript and notes text so the search layer can build
    snippets for the frontend.

    Args:
        user_id: The authenticated user's ID.
        query: The search term provided by the user.

    Returns:
        A list of matching session dictionaries ordered by most recent first.
    """
    like_query = f"%{query}%"

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT
                s.*,
                t.content AS transcript_content,
                n.summary AS notes_summary,
                n.topics AS notes_topics,
                n.action_items AS notes_action_items
            FROM sessions AS s
            JOIN course_members AS cm ON s.course_id = cm.course_id
            LEFT JOIN transcripts AS t ON t.session_id = s.id
            LEFT JOIN notes AS n ON n.session_id = s.id
            WHERE cm.user_id = ?
              AND (
                    s.title LIKE ?
                    OR COALESCE(t.content, '') LIKE ?
                    OR COALESCE(n.summary, '') LIKE ?
                    OR COALESCE(n.topics, '') LIKE ?
                    OR COALESCE(n.action_items, '') LIKE ?
                  )
            ORDER BY s.id DESC
            """,
            (user_id, like_query, like_query, like_query, like_query, like_query),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]