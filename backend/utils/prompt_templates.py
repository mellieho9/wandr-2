"""
Prompt templates for Gemini AI service.
Contains golden examples and base prompts for schema analysis.
"""

GOLDEN_EXAMPLE_PROMPT = """Analyze video content and extract comprehensive information to populate the following Notion database fields:

**Schema Fields:**
- Place (title) - The business/location name
- Address (rich_text) - Full address
- Category (select) - One of: Restaurant, Bakery, Dessert, Cafe, Workshop, Stationery
- Tags (select) - Additional categorization tags
- Is popup (checkbox) - Whether this is a temporary/popup location
- Coordinate (place) - Geographic coordinates if available
- Tiktok URL (url) - Source video URL
- Availability (rich_text) - Hours, schedule, or temporal availability
- Recommendations (rich_text) - Specific menu items, products, or highlights

**Extraction Strategy:**

Handle these edge cases:

1. **Single Places**: One restaurant/business featured in the video
2. **Multiple Places**: Area guides or videos featuring multiple locations
3. **Popup Events**: Temporary events, markets, or limited-time restaurants
4. **Carousel Content**: Multiple images with different text/locations per image
5. **Market Vendors**: Individual vendors/stalls within food courts, farmer's markets, flea markets, night markets
6. **Non-English Names**: Places with Chinese, Korean, Japanese, or other non-English names

**IMPORTANT**: Pay special attention to:
- Chinese characters or non-English place names (e.g., 满小满, 老友记, etc.)
- Market references ("inside [mall name] food court", "stall in", "vendor at", "farmer's market", "flea market", "night market")
- Address information mentioned in hashtags or location descriptions
- Mall, plaza, or market names that contain the individual vendors

Extract information in this EXACT JSON format matching the Notion schema:
{{
    "places": [
        {{
            "Place": "Business/Restaurant Name (title field)",
            "Address": "Full street address if mentioned (rich_text)",
            "Category": "Restaurant|Bakery|Dessert|Cafe|Workshop|Stationery (select - must be exact match)",
            "Tags": "cuisine type, neighborhood, or other tag (select)",
            "Is popup": false,
            "Coordinate": "geographic coordinates or location pin if available (place field)",
            "Tiktok URL": "source video URL (url field)",
            "Availability": "Opening hours, schedule, 'weekends only', 'until Dec 31', etc. (rich_text)",
            "Recommendations": "Specific menu items, signature dishes, must-try products (rich_text)"
        }}
    ],
}}

**CRITICAL INSTRUCTIONS**:
- **Place field (title)**: MUST be a specific, identifiable business name - NO generic terms like "restaurant", "cafe", "unnamed", etc.
- **Category field (select)**: MUST exactly match one of: Restaurant, Bakery, Dessert, Cafe, Workshop, or Stationery
- **Tags field (select)**: Use for cuisine type, neighborhood, or other categorization (e.g., "Chinese", "Downtown", "Fine Dining")
- **Is popup field (checkbox)**: Set to true for temporary locations, popup events, limited-time vendors, seasonal markets
- **Availability field (rich_text)**: Include specific hours if mentioned, or temporal indicators like "weekends only", "until Jan 15", "Fridays 5-9pm"
- **Recommendations field (rich_text)**: Extract SPECIFIC items - "truffle fries", "matcha latte", "almond croissants" NOT generic "food", "drinks", "desserts"
- **Address field (rich_text)**: Full street address; for market vendors include market name ("Stand 5, Union Square Farmer's Market, 123 Main St")
- **Coordinate field (place)**: Include if geographic coordinates or Notion location pin data is available
- **Tiktok URL field (url)**: The source video URL
- For popups: Set "Is popup"=true AND describe duration/schedule in "Availability" field
- For area guides with multiple places: Create separate entries in the places array for each location
- If no specific business name available: Return empty places array
- ALWAYS extract Chinese/Korean/Japanese/non-English place names - they are VALID business names (e.g., 满小满, 老友记)
- For market vendors WITH names: Use actual vendor name in "Place" field + market address in "Address" field
- For market vendors WITHOUT names: Format "Place" as "Corner Stall at [Market Name]" or "Booth A12 at [Market Name]"
- Look for location clues in: video text overlays (OCR), spoken transcription, hashtags, 📍 location pins, video descriptions
- Use exact JSON field names matching the Notion schema: Place, Address, Category, Tags, Is popup, Coordinate, Tiktok URL, Availability, Recommendations"""


def create_schema_analysis_prompt(
    properties_text: str, tag: str, user_feedback: str = None
) -> str:
    """
    Creates a prompt for Gemini to analyze the Notion schema and generate mapping instructions.

    Args:
        properties_text: Formatted string of schema properties
        tag: The tag/category for this database
        user_feedback: Optional feedback from user to refine the prompt

    Returns:
        A formatted prompt for Gemini
    """
    base_prompt = f"""You are an expert at analyzing database schemas and creating content mapping instructions.

I have a Notion database with the tag "{tag}" that has the following schema:

{properties_text}

This database will be populated with content extracted from videos, including:
- Video transcriptions (text extracted from audio)
- OCR content (text extracted from visual frames)
- Video metadata (title, description, etc.)

Your task is to generate a clear, concise prompt that describes how to intelligently map the video content to this schema. The prompt will be used by an AI system to automatically populate the Notion database fields based on the video content.

Guidelines for your response:
1. Identify which fields should be populated and suggest how
2. Consider semantic relationships between video content and schema fields
3. Be specific about extraction strategies (e.g., summarization, keyword extraction, categorization)
4. Keep it concise and actionable (2-4 sentences per field max)
5. Focus on automation - the prompt will be used programmatically

GOLDEN EXAMPLE:
Here's an example of a comprehensive, well-structured mapping prompt that handles edge cases and provides clear extraction strategies:

"{GOLDEN_EXAMPLE_PROMPT}"

Your mapping instructions should be similarly comprehensive, handling edge cases specific to your schema and providing clear extraction rules."""

    if user_feedback:
        base_prompt += f"""

IMPORTANT - USER FEEDBACK:
The user has provided the following feedback to refine the mapping instructions:
"{user_feedback}"

Please incorporate this feedback into your mapping instructions."""

    base_prompt += "\n\nGenerate the mapping instructions now:"

    return base_prompt
