import requests
import os
import json
import logging

logger = logging.getLogger("webtapi.ai")

# Configuration
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:5000")

def parse_query(query: str) -> dict:
    """Convert natural language to extraction instructions"""
    # Fallback response
    default_response = {
        "elements": ["text", "images", "links"],
        "filters": {},
        "structured_format": "list"
    }
    
    if not AI_SERVER_URL:
        logger.warning("AI server URL not configured, using default extraction")
        return default_response
    
    prompt = f"""
    Convert this website extraction request to structured instructions:
    "{query}"
    
    Respond ONLY with valid JSON in this format:
    {{
        "elements": ["text", "images", "tables", "links", "custom"],
        "filters": {{
            "include_selectors": ["css.selectors.here"],
            "exclude_selectors": ["unwanted.selectors"]
        }},
        "structured_format": "list|dict|table"
    }}
    
    Guidelines:
    1. Only include relevant element types
    2. For custom elements, provide CSS selectors in include_selectors
    3. Choose structured_format that best fits the request
    4. NEVER include any explanatory text
    """
    
    try:
        response = requests.post(
            f"{AI_SERVER_URL}/api/v1/generate",
            json={
                "prompt": prompt,
                "max_new_tokens": 300,
                "temperature": 0.2,
                "stop": ["###", "\n\n"],
                "do_sample": False
            },
            timeout=20
        )
        
        if response.status_code != 200:
            logger.error(f"AI server error: {response.text}")
            return default_response
        
        # Extract JSON from response
        result_text = response.json()["results"][0]["text"].strip()
        
        # Find JSON in the response
        try:
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            return json.loads(result_text[json_start:json_end])
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return default_response
        
    except requests.exceptions.Timeout:
        logger.warning("AI server timed out")
        return default_response
    except Exception as e:
        logger.error(f"AI processing failed: {str(e)}")
        return default_response