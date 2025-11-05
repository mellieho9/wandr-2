"""
Social Video Processor - Main Flask Application
Monitors Notion Link Database for video URLs and processes them through
transcription, OCR, and summarization pipeline.
"""

from flask import Flask, request, jsonify, redirect
from config.settings import Settings
from utils.db import get_db, ensure_connected
import logging
import requests
import secrets
import asyncio

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

# Store OAuth state tokens temporarily (in production, use Redis or database)
oauth_states = {}


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
    try:
        logger.info("Notion OAuth login initiated")
        
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = True
        
        # Build Notion OAuth authorization URL
        auth_url = (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={settings.NOTION_CLIENT_ID}"
            f"&response_type=code"
            f"&owner=user"
            f"&redirect_uri={settings.NOTION_REDIRECT_URI}"
            f"&state={state}"
        )
        
        logger.info(f"Redirecting to Notion OAuth with state: {state}")
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Failed to initiate OAuth flow: {e}")
        return jsonify({"error": "Failed to initiate OAuth flow", "details": str(e)}), 500


@app.route('/auth/notion/callback', methods=['GET'])
def notion_callback():
    """
    Handles Notion OAuth callback.
    Exchanges authorization code for access token and stores user credentials.
    """
    try:
        logger.info("Notion OAuth callback received")
        
        # Get authorization code and state from query parameters
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        # Check for OAuth errors
        if error:
            logger.error(f"OAuth error: {error}")
            return jsonify({
                "error": "OAuth authorization failed",
                "details": error
            }), 400
        
        # Validate required parameters
        if not code or not state:
            logger.error("Missing code or state parameter")
            return jsonify({
                "error": "Missing required parameters",
                "details": "code and state are required"
            }), 400
        
        # Verify state to prevent CSRF attacks
        if state not in oauth_states:
            logger.error(f"Invalid state parameter: {state}")
            return jsonify({
                "error": "Invalid state parameter",
                "details": "State verification failed"
            }), 400
        
        # Remove used state
        del oauth_states[state]
        
        # Exchange authorization code for access token
        token_url = "https://api.notion.com/v1/oauth/token"
        auth_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.NOTION_REDIRECT_URI
        }
        
        logger.info("Exchanging authorization code for access token")
        response = requests.post(
            token_url,
            auth=(settings.NOTION_CLIENT_ID, settings.NOTION_CLIENT_SECRET),
            json=auth_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            return jsonify({
                "error": "Failed to exchange authorization code",
                "details": response.text
            }), 400
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        owner = token_data.get("owner", {})
        workspace_id = token_data.get("workspace_id")
        
        if not access_token:
            logger.error("No access token in response")
            return jsonify({
                "error": "No access token received",
                "details": "Token exchange succeeded but no token returned"
            }), 400
        
        # Extract user information
        user_type = owner.get("type")  # "user" or "workspace"
        if user_type == "user":
            oauth_id = owner.get("user", {}).get("id")
        else:
            oauth_id = workspace_id
        
        if not oauth_id:
            logger.error("Could not extract user ID from token response")
            return jsonify({
                "error": "Could not extract user ID",
                "details": "No user or workspace ID found"
            }), 400
        
        # Store user in database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        user = loop.run_until_complete(_create_or_update_user(oauth_id, access_token))
        loop.close()
        
        logger.info(f"User authenticated successfully: {user.id}")
        
        return jsonify({
            "success": True,
            "message": "Authentication successful",
            "user_id": user.id,
            "oauth_id": user.oauthId
        }), 200
        
    except requests.RequestException as e:
        logger.error(f"HTTP request failed during OAuth: {e}")
        return jsonify({
            "error": "OAuth request failed",
            "details": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {e}")
        return jsonify({
            "error": "Authentication failed",
            "details": str(e)
        }), 500


async def _create_or_update_user(oauth_id: str, access_token: str):
    """
    Create or update user in database with OAuth credentials.
    
    Args:
        oauth_id: Notion OAuth user ID
        access_token: Notion access token
        
    Returns:
        User object
    """
    await ensure_connected()
    db = get_db()
    
    # Check if user already exists
    existing_user = await db.user.find_unique(where={"oauthId": oauth_id})
    
    if existing_user:
        # Update existing user's token
        logger.info(f"Updating existing user: {oauth_id}")
        user = await db.user.update(
            where={"oauthId": oauth_id},
            data={"notionAccessToken": access_token}
        )
    else:
        # Create new user
        logger.info(f"Creating new user: {oauth_id}")
        user = await db.user.create(
            data={
                "oauthId": oauth_id,
                "notionAccessToken": access_token
            }
        )
    
    return user


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
