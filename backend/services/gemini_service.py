"""
Gemini AI Service for generating prompts based on Notion schemas.
Uses Google's Generative AI to create intelligent prompts for content mapping.
Supports iterative refinement through user feedback.
"""

import logging
from typing import Dict, Any, Tuple, Optional
import google.generativeai as genai

from config.settings import Settings
from utils.db import get_db, ensure_connected
from utils.prompt_templates import create_schema_analysis_prompt

logger = logging.getLogger(__name__)

# Initialize Gemini with API key
settings = Settings()
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Service for generating AI prompts using Google Gemini"""

    @staticmethod
    def _create_schema_analysis_prompt(
        schema_data: Dict[str, Any], tag: str, user_feedback: Optional[str] = None
    ) -> str:
        """
        Creates a prompt for Gemini to analyze the Notion schema and generate mapping instructions.

        Args:
            schema_data: The Notion database schema (properties)
            tag: The tag/category for this database
            user_feedback: Optional feedback from user to refine the prompt

        Returns:
            A formatted prompt for Gemini
        """
        # Extract property information
        properties_summary = []
        for prop_name, prop_info in schema_data.items():
            prop_type = prop_info.get("type", "unknown")
            properties_summary.append(f"  - {prop_name} ({prop_type})")

        properties_text = "\n".join(properties_summary)

        # Use the template function from prompt_templates.py
        return create_schema_analysis_prompt(properties_text, tag, user_feedback)

    @staticmethod
    async def generate_prompt_for_schema(
        user_id: int, tag: str, user_feedback: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Generate an AI prompt for a registered Notion schema using Gemini.

        Args:
            user_id: User ID from session
            tag: The tag identifying the schema to generate a prompt for
            user_feedback: Optional feedback from user to refine the generation

        Returns:
            Tuple of (response_dict, status_code)
        """
        await ensure_connected()
        db = get_db()

        try:
            # Get the schema for this user and tag
            schema = await db.notionschema.find_first(
                where={"userId": user_id, "tag": tag}
            )

            if not schema:
                return {"error": f"No schema found with tag '{tag}' for this user"}, 404

            # Create the analysis prompt
            analysis_prompt = GeminiService._create_schema_analysis_prompt(
                schema.schemaData, tag, user_feedback
            )

            # Call Gemini API
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(analysis_prompt)

            if not response or not response.text:
                return {"error": "Failed to generate prompt from Gemini"}, 500

            generated_prompt = response.text.strip()

            logger.info(
                "Generated prompt for schema: user_id=%s, tag=%s, with_feedback=%s, length=%d",
                user_id,
                tag,
                user_feedback is not None,
                len(generated_prompt),
            )

            return {
                "tag": tag,
                "generated_prompt": generated_prompt,
                "schema_id": schema.id,
            }, 200

        except Exception as e:
            logger.error("Error generating prompt with Gemini: %s", e)
            return {"error": f"Failed to generate prompt: {str(e)}"}, 500

    @staticmethod
    async def generate_and_save_prompt(
        user_id: int, tag: str, user_feedback: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Generate an AI prompt for a schema and save it to the database.

        Args:
            user_id: User ID from session
            tag: The tag identifying the schema
            user_feedback: Optional feedback from user to refine the generation

        Returns:
            Tuple of (response_dict, status_code)
        """
        await ensure_connected()
        db = get_db()

        try:
            # First generate the prompt
            result, status = await GeminiService.generate_prompt_for_schema(
                user_id, tag, user_feedback
            )

            if status != 200:
                return result, status

            generated_prompt = result["generated_prompt"]
            schema_id = result["schema_id"]

            # Update the schema with the generated prompt
            updated_schema = await db.notionschema.update(
                where={"id": schema_id}, data={"prompt": generated_prompt}
            )

            logger.info(
                "Saved generated prompt for schema: user_id=%s, tag=%s, schema_id=%s",
                user_id,
                tag,
                schema_id,
            )

            return {
                "message": "Prompt generated and saved successfully",
                "tag": tag,
                "prompt": updated_schema.prompt,
                "schema_id": updated_schema.id,
            }, 200

        except Exception as e:
            logger.error("Error saving generated prompt: %s", e)
            return {"error": f"Failed to save prompt: {str(e)}"}, 500

    @staticmethod
    async def update_prompt(
        user_id: int, tag: str, custom_prompt: str
    ) -> Tuple[Dict[str, Any], int]:
        """
        Update the prompt for a schema with a custom value.

        Args:
            user_id: User ID from session
            tag: The tag identifying the schema
            custom_prompt: The custom prompt text

        Returns:
            Tuple of (response_dict, status_code)
        """
        await ensure_connected()
        db = get_db()

        try:
            # Get the schema
            schema = await db.notionschema.find_first(
                where={"userId": user_id, "tag": tag}
            )

            if not schema:
                return {"error": f"No schema found with tag '{tag}' for this user"}, 404

            # Update with custom prompt
            updated_schema = await db.notionschema.update(
                where={"id": schema.id}, data={"prompt": custom_prompt}
            )

            logger.info(
                "Updated custom prompt for schema: user_id=%s, tag=%s",
                user_id,
                tag,
            )

            return {
                "message": "Prompt updated successfully",
                "tag": tag,
                "prompt": updated_schema.prompt,
            }, 200

        except Exception as e:
            logger.error("Error updating custom prompt: %s", e)
            return {"error": f"Failed to update prompt: {str(e)}"}, 500

    @staticmethod
    async def get_prompt(user_id: int, tag: str) -> Tuple[Dict[str, Any], int]:
        """
        Get the current prompt for a schema.

        Args:
            user_id: User ID from session
            tag: The tag identifying the schema

        Returns:
            Tuple of (response_dict, status_code)
        """
        await ensure_connected()
        db = get_db()

        try:
            schema = await db.notionschema.find_first(
                where={"userId": user_id, "tag": tag}
            )

            if not schema:
                return {"error": f"No schema found with tag '{tag}' for this user"}, 404

            return {
                "tag": tag,
                "prompt": schema.prompt,
                "has_prompt": schema.prompt is not None,
                "schema_id": schema.id,
            }, 200

        except Exception as e:
            logger.error("Error retrieving prompt: %s", e)
            return {"error": f"Failed to retrieve prompt: {str(e)}"}, 500
