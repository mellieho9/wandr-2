"""
Database service for Content and Link Database operations.
Handles business logic for database registration and retrieval.
"""

import logging
from typing import Dict, Any, Tuple

from clients.notion_client import NotionClient, NotionAPIError
from utils.db import get_db, ensure_connected

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing Content and Link Database operations"""

    @staticmethod
    async def register_content_database(
        user_id: int, db_id: str, tag: str, prompt: str = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Register a Content Database with schema and tag.

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

            logger.info(
                "Schema data properties: %s",
                list(schema_data.get("properties", {}).keys()),
            )

            # Store schema in database
            # Pass the dict directly - Prisma will handle JSON serialization
            create_data = {
                "userId": user_id,
                "dbId": db_id,
                "tag": tag,
                "schemaData": schema_data["properties"],
            }

            if prompt:
                create_data["prompt"] = prompt

            # Use execute_raw to bypass GraphQL parsing issues with special characters in JSON keys
            import json

            schema_json_str = json.dumps(schema_data["properties"])

            notion_schema = await db.query_raw(
                f"""
                INSERT INTO notion_schemas (user_id, db_id, tag, schema, prompt, created_at, updated_at)
                VALUES ($1, $2, $3, $4::jsonb, $5, NOW(), NOW())
                RETURNING id, user_id, db_id, tag, schema, prompt, created_at, updated_at
                """,
                user_id,
                db_id,
                tag,
                schema_json_str,
                prompt,
            )

            if not notion_schema or len(notion_schema) == 0:
                raise Exception("Failed to insert schema into database")

            logger.info(
                "Content Database registered: user_id=%s, tag=%s, db_id=%s",
                user_id,
                tag,
                db_id,
            )

            schema_record = notion_schema[0]
            return {
                "message": "Content Database registered successfully",
                "schema": {
                    "id": schema_record["id"],
                    "db_id": schema_record["db_id"],
                    "tag": schema_record["tag"],
                    "prompt": schema_record["prompt"],
                },
            }, 201

        except NotionAPIError as e:
            logger.error("Failed to retrieve database schema: %s", e)
            return {"error": f"Failed to retrieve database schema: {str(e)}"}, 400

    @staticmethod
    async def list_registered_databases(user_id: int) -> Tuple[Dict[str, Any], int]:
        """
        List all registered Content Databases for a user.

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
                    "schema": schema.schemaData,
                    "prompt": schema.prompt,
                    "created_at": schema.createdAt.isoformat()
                    if schema.createdAt
                    else None,
                }
            )

        logger.info("Listed %d databases for user_id=%s", len(databases), user_id)

        return {"databases": databases}, 200

    @staticmethod
    async def list_available_databases(user_id: int) -> Tuple[Dict[str, Any], int]:
        """
        List all databases available in user's Notion workspace.

        Args:
            user_id: User ID from session

        Returns:
            Tuple of (response_dict, status_code)
        """
        await ensure_connected()
        db = get_db()

        # Get user and access token
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            return {"error": "User not found"}, 404

        # Get databases from Notion
        try:
            notion_client = NotionClient(user.notionAccessToken)
            databases = notion_client.get_databases()

            logger.info(
                "Listed %d available databases for user_id=%s", len(databases), user_id
            )

            return {"databases": databases}, 200

        except NotionAPIError as e:
            logger.error("Failed to retrieve available databases: %s", e)
            return {"error": f"Failed to retrieve available databases: {str(e)}"}, 400

    @staticmethod
    async def register_link_database(
        user_id: int, db_id: str
    ) -> Tuple[Dict[str, Any], int]:
        """
        Register user's Link Database for monitoring.

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
            required_fields = [
                "url",
                "tag",
                "processing_type",
                "status",
                "updated_time",
            ]
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

            logger.info(
                "Link Database registered: user_id=%s, db_id=%s", user_id, db_id
            )

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
