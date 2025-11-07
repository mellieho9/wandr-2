"""
Authentication endpoints for Notion OAuth flow
"""

import logging
import secrets

import requests
from flask import Blueprint, request, jsonify, redirect

from config.settings import Settings
from services.auth_service import AuthService
from utils.redis_client import get_redis_client

logger = logging.getLogger(__name__)

# Create Blueprint for auth endpoints
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Initialize dependencies
settings = Settings()
redis_client = get_redis_client()
auth_service = AuthService()


@auth_bp.route("/notion/login", methods=["GET"])
def notion_login():
    """
    Initiates Notion OAuth flow.
    Redirects user to Notion authorization page.
    """
    try:
        logger.info("Notion OAuth login initiated")

        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state in Redis with 5-minute TTL (auto-expiration)
        # Falls back to in-memory storage if Redis is unavailable
        redis_client.set_with_ttl(f"oauth_state:{state}", "pending", ttl_seconds=300)

        # Build Notion OAuth authorization URL
        auth_url = (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={settings.NOTION_CLIENT_ID}"
            f"&response_type=code"
            f"&owner=user"
            f"&redirect_uri={settings.NOTION_REDIRECT_URI}"
            f"&state={state}"
        )

        logger.info("Redirecting to Notion OAuth with state: %s", state)
        return redirect(auth_url)

    except Exception as e:
        logger.error("Failed to initiate OAuth flow: %s", e)
        return jsonify(
            {"error": "Failed to initiate OAuth flow", "details": str(e)}
        ), 500


@auth_bp.route("/notion/callback", methods=["GET"])
def notion_callback():
    """
    Handles Notion OAuth callback.
    Exchanges authorization code for access token and stores user credentials.
    """
    try:
        logger.info("Notion OAuth callback received")

        # Get authorization code and state from query parameters
        code = request.args.get("code")
        state = request.args.get("state")
        error = request.args.get("error")

        # Check for OAuth errors
        if error:
            logger.error("OAuth error: %s", error)
            return jsonify(
                {"error": "OAuth authorization failed", "details": error}
            ), 400

        # Validate required parameters
        if not code or not state:
            logger.error("Missing code or state parameter")
            return jsonify(
                {
                    "error": "Missing required parameters",
                    "details": "code and state are required",
                }
            ), 400

        # Verify state to prevent CSRF attacks
        state_key = f"oauth_state:{state}"
        if not redis_client.exists(state_key):
            logger.error("Invalid state parameter: %s", state)
            return jsonify(
                {
                    "error": "Invalid state parameter",
                    "details": "State verification failed",
                }
            ), 400

        # Remove used state from Redis (or in-memory fallback)
        redis_client.delete(state_key)

        # Exchange authorization code for access token
        token_data = auth_service.exchange_code_for_token(code)

        if not token_data:
            return jsonify({"error": "Failed to exchange authorization code"}), 400

        # Extract user information and store in database
        user = auth_service.create_or_update_user_from_token(token_data)

        if not user:
            return jsonify({"error": "Failed to create or update user"}), 400

        logger.info("User authenticated successfully: %s", user.id)

        # Store user_id in session for subsequent API calls
        from flask import session

        session["user_id"] = user.id

        # Redirect to frontend with success parameters
        return redirect(f"/?success=true&user_id={user.id}")

    except requests.RequestException as e:
        logger.error("HTTP request failed during OAuth: %s", e)
        return jsonify({"error": "OAuth request failed", "details": str(e)}), 500
    except Exception as e:
        logger.error("Unexpected error in OAuth callback: %s", e)
        return jsonify({"error": "Authentication failed", "details": str(e)}), 500
