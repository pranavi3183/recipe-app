"""
LLM service that uses Google Gemini (via LangChain) to:
- Extract structured recipe data from scraped text
- Generate meal plan merged shopping lists
"""

import json
import logging
import os
import re
from typing import Dict, Any, List

from dotenv import load_dotenv
from json_repair import repair_json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from google.api_core.exceptions import ResourceExhausted, PermissionDenied, Unauthenticated

from prompts.templates import RECIPE_EXTRACTION_PROMPT, MEAL_PLAN_PROMPT

load_dotenv()
logger = logging.getLogger(__name__)


def _get_llm() -> ChatGoogleGenerativeAI:
    """Initialize and return the Gemini LLM instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add your key to backend/.env"
        )
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",  # Free tier model with higher quota
        google_api_key=api_key,
        temperature=0.2,            # Low temp for factual extraction
        max_output_tokens=20000,
    )


def _parse_json_response(raw: str) -> Dict[str, Any]:
    """
    Safely parse JSON from LLM response.
    Handles markdown code fences, extra text, and truncated/malformed JSON
    via json-repair as a fallback.
    """
    # Strip markdown fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find JSON object boundaries and try again
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except json.JSONDecodeError:
            pass

    # Last resort: use json-repair to fix truncated / malformed JSON
    try:
        candidate = cleaned[start:] if start != -1 else cleaned
        repaired = repair_json(candidate, return_objects=True)
        if isinstance(repaired, dict) and repaired:
            logger.warning("LLM returned malformed JSON — recovered with json-repair")
            return repaired
    except Exception:
        pass

    logger.error(f"Failed to parse LLM JSON response:\n{raw[:1000]}")
    raise ValueError("LLM returned invalid JSON. Please try again.")


def extract_recipe_from_text(scraped_text: str) -> Dict[str, Any]:
    """
    Send scraped webpage text to Gemini and extract structured recipe data.
    
    Returns a dict matching the RecipeCreate schema.
    Raises ValueError on API errors or invalid responses.
    """
    llm = _get_llm()
    chain = LLMChain(llm=llm, prompt=RECIPE_EXTRACTION_PROMPT)

    logger.info("Sending scraped text to Gemini for extraction...")

    try:
        result = chain.invoke({"scraped_text": scraped_text})
        raw_output = result.get("text", "")
    except (ResourceExhausted, PermissionDenied, Unauthenticated) as e:
        logger.error(f"Gemini API quota/auth error: {e}")
        raise ValueError(
            "Gemini API key has no quota or is invalid. "
            "Get a free key at https://aistudio.google.com/app/apikey and update backend/.env"
        )
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        raise ValueError(f"LLM API error: {str(e)}")

    parsed = _parse_json_response(raw_output)

    # Ensure required keys exist with defaults
    defaults = {
        "title": None,
        "cuisine": None,
        "prep_time": None,
        "cook_time": None,
        "total_time": None,
        "servings": None,
        "difficulty": None,
        "ingredients": [],
        "instructions": [],
        "nutrition_estimate": {},
        "substitutions": [],
        "shopping_list": {},
        "related_recipes": [],
    }
    for key, default in defaults.items():
        parsed.setdefault(key, default)

    return parsed


def generate_meal_plan(recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Given a list of recipe dicts, generate a merged meal plan shopping list.
    
    Returns a dict with merged_shopping_list and tips.
    """
    llm = _get_llm()
    chain = LLMChain(llm=llm, prompt=MEAL_PLAN_PROMPT)

    # Build compact recipe summary for the prompt
    recipes_summary = []
    for r in recipes:
        recipes_summary.append({
            "title": r.get("title", "Unknown"),
            "ingredients": r.get("ingredients", []),
        })

    recipes_json = json.dumps(recipes_summary, indent=2)

    logger.info(f"Generating meal plan for {len(recipes)} recipes...")

    try:
        result = chain.invoke({"recipes_json": recipes_json})
        raw_output = result.get("text", "")
    except (ResourceExhausted, PermissionDenied, Unauthenticated) as e:
        logger.error(f"Gemini API quota/auth error: {e}")
        raise ValueError(
            "Gemini API key has no quota or is invalid. "
            "Get a free key at https://aistudio.google.com/app/apikey and update backend/.env"
        )
    except Exception as e:
        raise ValueError(f"LLM API error during meal plan generation: {str(e)}")

    return _parse_json_response(raw_output)
