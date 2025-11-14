"""
Prompt generation endpoints for AI-powered content mapping.
Handles generation, refinement, and management of prompts for Notion schemas.
"""

import asyncio
import logging
from flask import Blueprint, jsonify, request, session

from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Create Blueprint for prompt endpoints
prompts_bp = Blueprint("prompts", __name__, url_prefix="/api/prompts")


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


@prompts_bp.route("/generate/<tag>", methods=["POST"])
def generate_prompt(tag):
    """
    Generate an AI prompt for a schema (initial generation or with feedback).
    Does not save to database - returns the generated prompt for user review.

    Request body (optional):
        {
            "feedback": "Make it more detailed and focus on summarization"
        }

    Response:
        {
            "tag": "tech-videos",
            "generated_prompt": "...",
            "schema_id": 123
        }
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Parse optional feedback from request body
        data = request.get_json() or {}
        user_feedback = data.get("feedback")

        # Call service layer
        result = run_async(
            GeminiService.generate_prompt_for_schema(user_id, tag, user_feedback)
        )

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error generating prompt: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@prompts_bp.route("/generate-and-save/<tag>", methods=["POST"])
def generate_and_save_prompt(tag):
    """
    Generate an AI prompt and immediately save it to the database.
    Use this when user approves the generated prompt.

    Request body (optional):
        {
            "feedback": "Make it more detailed"
        }

    Response:
        {
            "message": "Prompt generated and saved successfully",
            "tag": "tech-videos",
            "prompt": "...",
            "schema_id": 123
        }
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Parse optional feedback from request body
        data = request.get_json() or {}
        user_feedback = data.get("feedback")

        # Call service layer
        result = run_async(
            GeminiService.generate_and_save_prompt(user_id, tag, user_feedback)
        )

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error generating and saving prompt: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@prompts_bp.route("/<tag>", methods=["GET"])
def get_prompt(tag):
    """
    Get the current prompt for a schema.

    Response:
        {
            "tag": "tech-videos",
            "prompt": "..." or null,
            "has_prompt": true/false,
            "schema_id": 123
        }
    """
    try:
        # Get user_id from session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized - please login first"}), 401

        # Call service layer
        result = run_async(GeminiService.get_prompt(user_id, tag))

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error getting prompt: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@prompts_bp.route("/<tag>", methods=["PUT"])
def update_prompt(tag):
    """
    Update/save a prompt with custom text (manual edit or approved AI generation).

    Request body:
        {
            "prompt": "Custom mapping instructions..."
        }

    Response:
        {
            "message": "Prompt updated successfully",
            "tag": "tech-videos",
            "prompt": "..."
        }
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

        custom_prompt = data.get("prompt")
        if not custom_prompt:
            return jsonify({"error": "prompt is required"}), 400

        # Call service layer
        result = run_async(GeminiService.update_prompt(user_id, tag, custom_prompt))

        return jsonify(result[0]), result[1]

    except Exception as e:
        logger.error("Error updating prompt: %s", e)
        return jsonify({"error": "Internal server error"}), 500
