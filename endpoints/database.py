"""
Database management endpoints for Content and Link Databases
"""

import asyncio
import logging
from flask import Blueprint, jsonify, request, session

from clients.notion_client import NotionClient, NotionAPIError
from utils.db import get_db, ensure_connected

logger = logging.getLogger(__name__)

# Create Blueprint for database endpoints
database_bp = Blueprint("database", __name__, url_prefix="/api")


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

        # Get user's access token
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            _register_content_database_async(user_id, db_id, tag, prompt)
        )
        loop.close()

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error registering Content Database: %s", e)
        return jsonify({"error": "Internal server error"}), 500


async def _register_content_database_async(
    user_id: int, db_id: str, tag: str, prompt: str = None
):
    """
    Async helper to register Content Database.

    Args:
        user_id: User ID from session
        db_id: Notion database ID
        tag: Unique tag for this database
        prompt: Optional custom Schema Prompt

    Returns:
        Tuple of (response_dict, status_code)
    """
    await ensure_connected()
    db = get_db()

    # Get user and access token
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        return {"error": "User not found"}, 404

    # Check if tag is already used by this user
    existing_schema = await db.notionschema.find_first(
        where={"userId": user_id, "tag": tag}
    )
    if existing_schema:
        return {"error": f"Tag '{tag}' is already in use"}, 409

    # Retrieve database schema from Notion
    try:
        notion_client = NotionClient(user.notionAccessToken)
        schema_data = notion_client.get_database_schema(db_id)

        # Store schema in database
        notion_schema = await db.notionschema.create(
            data={
                "userId": user_id,
                "dbId": db_id,
                "tag": tag,
                "schema": schema_data["properties"],
                "prompt": prompt,
            }
        )

        logger.info(
            "Content Database registered: user_id=%s, tag=%s, db_id=%s",
            user_id,
            tag,
            db_id,
        )

        return {
            "message": "Content Database registered successfully",
            "schema": {
                "id": notion_schema.id,
                "db_id": notion_schema.dbId,
                "tag": notion_schema.tag,
                "prompt": notion_schema.prompt,
            },
        }, 201

    except NotionAPIError as e:
        logger.error("Failed to retrieve database schema: %s", e)
        return {"error": f"Failed to retrieve database schema: {str(e)}"}, 400


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

        # Get user's registered databases
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_list_databases_async(user_id))
        loop.close()

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error listing databases: %s", e)
        return jsonify({"error": "Internal server error"}), 500


async def _list_databases_async(user_id: int):
    """
    Async helper to list Content Databases.

    Args:
        user_id: User ID from session

    Returns:
        Tuple of (response_dict, status_code)
    """
    await ensure_connected()
    db = get_db()

    # Get user
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        return {"error": "User not found"}, 404

    # Get all registered Content Databases for this user
    schemas = await db.notionschema.find_many(
        where={"userId": user_id}, order={"createdAt": "desc"}
    )

    databases = []
    for schema in schemas:
        databases.append(
            {
                "id": schema.id,
                "db_id": schema.dbId,
                "tag": schema.tag,
                "schema": schema.schema,
                "prompt": schema.prompt,
                "created_at": schema.createdAt.isoformat()
                if schema.createdAt
                else None,
            }
        )

    logger.info("Listed %d databases for user_id=%s", len(databases), user_id)

    return {"databases": databases}, 200


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

        # Get user's access token and validate Link Database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_register_link_database_async(user_id, db_id))
        loop.close()

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error registering Link Database: %s", e)
        return jsonify({"error": "Internal server error"}), 500


async def _register_link_database_async(user_id: int, db_id: str):
    """
    Async helper to register Link Database.

    Args:
        user_id: User ID from session
        db_id: Notion database ID

    Returns:
        Tuple of (response_dict, status_code)
    """
    await ensure_connected()
    db = get_db()

    # Get user and access token
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        return {"error": "User not found"}, 404

    # Check if user already has a Link Database registered
    existing_link_db = await db.linkdatabase.find_unique(where={"userId": user_id})
    if existing_link_db:
        return {"error": "Link Database already registered for this user"}, 409

    # Validate Link Database has required fields
    try:
        notion_client = NotionClient(user.notionAccessToken)
        schema_data = notion_client.get_database_schema(db_id)

        # Check for required fields
        properties = schema_data.get("properties", {})
        required_fields = ["url", "tag", "processing_type", "status", "updated_time"]
        missing_fields = []

        for field in required_fields:
            if field not in properties:
                missing_fields.append(field)

        if missing_fields:
            return {
                "error": f"Link Database is missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields,
            }, 400

        # Validate field types
        field_types = {
            "url": "url",
            "tag": "select",
            "processing_type": "select",
            "status": "select",
            "updated_time": "date",
        }

        invalid_types = []
        for field, expected_type in field_types.items():
            actual_type = properties[field].get("type")
            if actual_type != expected_type:
                invalid_types.append(
                    f"{field} (expected {expected_type}, got {actual_type})"
                )

        if invalid_types:
            return {
                "error": f"Link Database has invalid field types: {', '.join(invalid_types)}"
            }, 400

        # Store Link Database
        link_database = await db.linkdatabase.create(
            data={
                "userId": user_id,
                "dbId": db_id,
            }
        )

        logger.info("Link Database registered: user_id=%s, db_id=%s", user_id, db_id)

        return {
            "message": "Link Database registered successfully",
            "link_database": {
                "id": link_database.id,
                "db_id": link_database.dbId,
            },
        }, 201

    except NotionAPIError as e:
        logger.error("Failed to validate Link Database: %s", e)
        return {"error": f"Failed to validate Link Database: {str(e)}"}, 400
