"""
Application entry point.

This module creates and configures the Flask application that powers
the backend API.

The backend acts as the coordination layer of the system:
- receives requests from the frontend
- validates and authorizes users
- routes requests to the appropriate service layer
- connects to the processing pipeline and database

Blueprints and their URL prefixes:
    /api/auth        — authentication and user identity
    /api/sessions    — upload and retrieve recordings
    /api/transcripts — access transcript data
    /api/notes       — access AI-generated notes
    /api/courses     — course creation and membership
    /api/search      — search sessions within user-accessible courses

This file intentionally does not implement business logic. Its role is
to assemble the application and wire together all components in a
centralized and maintainable way.
"""

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from forum_ai_notetaker.db import init_db

# Import route groups
from routes.auth import auth_bp
from routes.courses import courses_bp
from routes.notes import notes_bp
from routes.search import search_bp
from routes.sessions import sessions_bp
from routes.transcripts import transcripts_bp


def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    This function is responsible for:
    - initializing the database schema
    - configuring global settings (e.g., upload directory)
    - enabling CORS for frontend communication
    - registering all route blueprints

    Using an application factory pattern improves testability,
    modularity, and scalability by avoiding global state and
    allowing multiple app instances if needed.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__)

    # Enable cross-origin requests so the React frontend can
    # communicate with the backend during development.
    CORS(app)

    # Create database tables if they do not exist yet.
    init_db()

    # Resolve upload directory from the backend root so it stays stable
    # regardless of the process working directory.
    backend_root = Path(__file__).resolve().parent
    upload_folder = backend_root / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_folder)

    # Register API route groups.
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(transcripts_bp, url_prefix="/api/transcripts")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(search_bp, url_prefix="/api/search")

    @app.route("/", methods=["GET"])
    def home():
        """
        Root endpoint for basic API verification.

        This route prevents a 404 at the base URL and provides a simple
        confirmation that the backend server is running.

        Returns:
            A JSON message indicating the API status.
        """
        return {
            "message": "Backend API is running.",
            "hint": "Try /api/health to test the server.",
        }, 200

    @app.route("/api/health", methods=["GET"])
    def health():
        """
        Health check endpoint.

        This route is used during development and deployment to verify
        that the backend is running and reachable. It can also be used
        by monitoring tools or deployment platforms.

        Returns:
            A JSON response indicating system health.
        """
        return {
            "status": "ok",
            "message": "Backend is running",
        }, 200

    return app


# Create the Flask application instance
app = create_app()


if __name__ == "__main__":
    # Run the development server with auto-reload enabled.
    app.run(debug=True)