"""
Database management endpoints for Content and Link Databases
"""

import asyncio
import logging
from flask import Blueprint, jsonify, request, session

from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

# Create Blueprint for database endpoints
database_bp = Blueprint("database", __name__, url_prefix="/api")


def run_async(coro):
    """Helper to run async functions in Flask endpoints"""
    # Always create a fresh event loop for each request to avoid
    # "bound to a different event loop" errors with Prisma
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(coro)
        return result
    finally:
        # Don't close the loop immediately as Prisma might need it
        # Let it be garbage collected
        pass


@database_bp.route("/databases/register", methods=["POST"])
def register_content_database():
    """
    Registers a Content Database with schema and tag.
    Retrieves and stores database schema for content mapping.
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Parse request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        db_id = data.get("db_id")
        tag = data.get("tag")
        prompt = data.get("prompt")  # Optional custom Schema Prompt

        # Validate required fields
        if not db_id:
            return jsonify({"error": "db_id is required"}), 400
        if not tag:
            return jsonify({"error": "tag is required"}), 400

        # Call service layer
        result = run_async(
            DatabaseService.register_content_database(user_id, db_id, tag, prompt)
        )

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error registering Content Database: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@database_bp.route("/databases", methods=["GET"])
def list_databases():
    """
    Lists all registered Content Databases for authenticated user.
    Returns db_id, tag, schema, and prompt for each database.
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Call service layer
        result = run_async(
            DatabaseService.list_registered_databases(user_id)
        )

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error listing databases: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@database_bp.route("/databases/available", methods=["GET"])
def list_available_databases():
    """
    Lists all databases available/shared with the authenticated user in Notion.
    This helps users discover which databases they can register.
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Call service layer
        result = run_async(
            DatabaseService.list_available_databases(user_id)
        )

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error listing available databases: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@database_bp.route("/link-database/register", methods=["POST"])
def register_link_database():
    """
    Registers user's Link Database for monitoring.
    Validates required fields and stores database ID.
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Parse request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        db_id = data.get("db_id")

        # Validate required fields
        if not db_id:
            return jsonify({"error": "db_id is required"}), 400

        # Call service layer
        result = run_async(
            DatabaseService.register_link_database(user_id, db_id)
        )

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error registering Link Database: %s", e)
        return jsonify({"error": "Internal server error"}), 500
