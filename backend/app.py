"""
Social Video Processor - Main Flask Application
Monitors Notion Link Database for video URLs and processes them through
transcription, OCR, and summarization pipeline.
"""

import logging
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config.settings import Settings
from utils.redis_client import get_redis_client
from endpoints.auth import auth_bp
from endpoints.database import database_bp
from endpoints.health import health_bp
from endpoints.prompts import prompts_bp

# Initialize Flask application
# Set static folder to serve frontend build files (relative to backend/)
app = Flask(__name__, static_folder="../frontend/build", static_url_path="")

# Load configuration
settings = Settings()
app.config["SECRET_KEY"] = settings.FLASK_SECRET_KEY

# Enable CORS for development (frontend dev server runs on different port)
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Redis client for OAuth state storage
# Falls back to in-memory storage if Redis is unavailable
redis_client = get_redis_client()
logger.info(
    "OAuth state storage initialized (Redis available: %s)", redis_client.is_available()
)

# Register blueprints
app.register_blueprint(health_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(database_bp)
app.register_blueprint(prompts_bp)


@app.route("/")
def serve_frontend():
    """Serve the React frontend"""
    frontend_build = os.path.join(app.static_folder or "", "index.html")
    if os.path.exists(frontend_build):
        return send_from_directory(app.static_folder or "", "index.html")
    else:
        return jsonify(
            {
                "message": "Frontend not built yet",
                "instructions": "Run 'cd frontend && npm install && npm run build' to build the frontend",
            }
        ), 404


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files or fallback to index.html for client-side routing"""
    frontend_build = app.static_folder or ""
    file_path = os.path.join(frontend_build, path)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(frontend_build, path)
    else:
        # Fallback to index.html for client-side routing
        index_path = os.path.join(frontend_build, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(frontend_build, "index.html")
        return jsonify({"error": "Not found"}), 404


@app.errorhandler(404)
def not_found(_error):
    """Handle 404 errors for API routes"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error("Internal server error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Run Flask development server
    app.run(host="0.0.0.0", port=8080, debug=(settings.FLASK_ENV == "development"))
