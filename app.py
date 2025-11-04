"""
Social Video Processor - Main Flask Application
Monitors Notion Link Database for video URLs and processes them through
transcription, OCR, and summarization pipeline.
"""

from flask import Flask, request, jsonify, redirect
from config.settings import Settings
import logging

# Initialize Flask application
app = Flask(__name__)

# Load configuration
settings = Settings()
app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Cloud Run monitoring.
    Returns service status and connectivity checks.
    """
    return jsonify({
        "status": "healthy",
        "service": "social-video-processor",
        "version": "1.0.0"
    }), 200


@app.route('/auth/notion/login', methods=['GET'])
def notion_login():
    """
    Initiates Notion OAuth flow.
    Redirects user to Notion authorization page.
    """
    # TODO: Implement OAuth flow initiation
    logger.info("Notion OAuth login initiated")
    return jsonify({"message": "OAuth flow not yet implemented"}), 501


@app.route('/auth/notion/callback', methods=['POST'])
def notion_callback():
    """
    Handles Notion OAuth callback.
    Exchanges authorization code for access token and stores user credentials.
    """
    # TODO: Implement OAuth callback handler
    logger.info("Notion OAuth callback received")
    return jsonify({"message": "OAuth callback not yet implemented"}), 501


@app.route('/api/databases/register', methods=['POST'])
def register_content_database():
    """
    Registers a Content Database with schema and tag.
    Retrieves and stores database schema for content mapping.
    """
    # TODO: Implement Content Database registration
    logger.info("Content Database registration requested")
    return jsonify({"message": "Database registration not yet implemented"}), 501


@app.route('/api/databases', methods=['GET'])
def list_databases():
    """
    Lists all registered Content Databases for authenticated user.
    Returns db_id, tag, schema, and prompt for each database.
    """
    # TODO: Implement database listing
    logger.info("Database listing requested")
    return jsonify({"databases": []}), 200


@app.route('/api/link-database/register', methods=['POST'])
def register_link_database():
    """
    Registers user's Link Database for monitoring.
    Validates required fields and stores database ID.
    """
    # TODO: Implement Link Database registration
    logger.info("Link Database registration requested")
    return jsonify({"message": "Link Database registration not yet implemented"}), 501


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Run Flask development server
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=(settings.FLASK_ENV == 'development')
    )
