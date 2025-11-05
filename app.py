"""
Social Video Processor - Main Flask Application
Monitors Notion Link Database for video URLs and processes them through
transcription, OCR, and summarization pipeline.
"""

import logging

from flask import Flask, jsonify

from config.settings import Settings
from utils.redis_client import get_redis_client
from endpoints.auth import auth_bp
from endpoints.database import database_bp
from endpoints.health import health_bp

# Initialize Flask application
app = Flask(__name__)

# Load configuration
settings = Settings()
app.config["SECRET_KEY"] = settings.FLASK_SECRET_KEY

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


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error("Internal server error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Run Flask development server
    app.run(host="0.0.0.0", port=8080, debug=(settings.FLASK_ENV == "development"))
