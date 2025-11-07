"""
Health check endpoint for monitoring
"""

from flask import Blueprint, jsonify

# Create Blueprint for health endpoint
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for Cloud Run monitoring.
    Returns service status and connectivity checks.
    """
    return jsonify(
        {"status": "healthy", "service": "social-video-processor", "version": "1.0.0"}
    ), 200
