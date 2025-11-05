"""
Authentication service for Notion OAuth
Handles token exchange and user management
"""

import asyncio
import logging
from typing import Optional, Dict, Any

import requests

from config.settings import Settings
from utils.db import get_db, ensure_connected

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling Notion OAuth authentication"""

    def __init__(self):
        """Initialize auth service with settings"""
        self.settings = Settings()

    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token data dictionary or None if exchange fails
        """
        token_url = "https://api.notion.com/v1/oauth/token"
        auth_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.NOTION_REDIRECT_URI,
        }

        try:
            logger.info("Exchanging authorization code for access token")
            response = requests.post(
                token_url,
                auth=(
                    self.settings.NOTION_CLIENT_ID,
                    self.settings.NOTION_CLIENT_SECRET,
                ),
                json=auth_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code != 200:
                logger.error("Token exchange failed: %s", response.text)
                return None

            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                logger.error("No access token in response")
                return None

            return token_data

        except requests.RequestException as e:
            logger.error("HTTP request failed during token exchange: %s", e)
            return None

    def create_or_update_user_from_token(self, token_data: Dict[str, Any]):
        """
        Create or update user in database from token data.

        Args:
            token_data: Token response from Notion OAuth

        Returns:
            User object or None if operation fails
        """
        try:
            access_token = token_data.get("access_token")
            owner = token_data.get("owner", {})
            workspace_id = token_data.get("workspace_id")

            # Extract user information
            user_type = owner.get("type")  # "user" or "workspace"
            if user_type == "user":
                oauth_id = owner.get("user", {}).get("id")
            else:
                oauth_id = workspace_id

            if not oauth_id:
                logger.error("Could not extract user ID from token response")
                return None

            # Store user in database
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            user = loop.run_until_complete(
                self._create_or_update_user(oauth_id, access_token)
            )
            loop.close()

            return user

        except Exception as e:
            logger.error("Failed to create or update user: %s", e)
            return None

    async def _create_or_update_user(self, oauth_id: str, access_token: str):
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
            logger.info("Updating existing user: %s", oauth_id)
            user = await db.user.update(
                where={"oauthId": oauth_id}, data={"notionAccessToken": access_token}
            )
        else:
            # Create new user
            logger.info("Creating new user: %s", oauth_id)
            user = await db.user.create(
                data={"oauthId": oauth_id, "notionAccessToken": access_token}
            )

        return user
