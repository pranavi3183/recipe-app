"""
LangChain prompt templates for recipe extraction and generation tasks.
Prompts are carefully designed to minimize hallucination by grounding
outputs strictly in the scraped page content.
"""

from langchain.prompts import PromptTemplate


# ─────────────────────────────────────────────
# PROMPT 1: Full Recipe Extraction + Enrichment
# ─────────────────────────────────────────────
RECIPE_EXTRACTION_TEMPLATE = """You are a culinary data extraction expert. 
Your job is to parse raw webpage text and return a clean, structured JSON object.

IMPORTANT RULES:
- Extract ONLY information that appears in the provided text. Do NOT invent data.
- If a field is not present, use null.
- For nutrition, provide a reasonable estimate based on standard culinary knowledge for the identified ingredients.
- Difficulty: "easy" if < 30 min and < 8 ingredients, "hard" if > 90 min or complex techniques, else "medium".
- Return ONLY valid JSON. No markdown fences, no explanation, no preamble.

SCRAPED PAGE CONTENT:
\"\"\"
{scraped_text}
\"\"\"

Return a JSON object with EXACTLY this structure:
{{
  "title": "string or null",
  "cuisine": "string (e.g. Italian, Mexican, American) or null",
  "prep_time": "string (e.g. '10 mins') or null",
  "cook_time": "string (e.g. '20 mins') or null",
  "total_time": "string (e.g. '30 mins') or null",
  "servings": integer or null,
  "difficulty": "easy" | "medium" | "hard" | null,
  "ingredients": [
    {{"quantity": "string", "unit": "string", "item": "string"}}
  ],
  "instructions": ["step 1 text", "step 2 text"],
  "nutrition_estimate": {{
    "calories": integer,
    "protein": "string (e.g. '12g')",
    "carbs": "string (e.g. '30g')",
    "fat": "string (e.g. '10g')"
  }},
  "substitutions": [
    "Replace X with Y for Z benefit.",
    "Replace A with B for C benefit.",
    "Replace D with E for F benefit."
  ],
  "shopping_list": {{
    "dairy": ["item1", "item2"],
    "produce": ["item1"],
    "pantry": ["item1"],
    "bakery": ["item1"],
    "meat": ["item1"],
    "spices": ["item1"]
  }},
  "related_recipes": ["Recipe Name 1", "Recipe Name 2", "Recipe Name 3"]
}}
"""

RECIPE_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["scraped_text"],
    template=RECIPE_EXTRACTION_TEMPLATE
)


# ─────────────────────────────────────────────
# PROMPT 2: Meal Plan Combined Shopping List
# ─────────────────────────────────────────────
MEAL_PLAN_TEMPLATE = """You are a meal planning assistant. 
Given a list of recipes and their ingredients, generate a MERGED shopping list with consolidated quantities.

RULES:
- Combine duplicate ingredients (e.g., two recipes needing butter → sum the amounts).
- Group by category: dairy, produce, pantry, bakery, meat, spices, other.
- Return ONLY valid JSON. No markdown, no explanation.

RECIPES:
{recipes_json}

Return this JSON structure:
{{
  "plan_title": "Weekly Meal Plan",
  "recipes_included": ["Recipe 1", "Recipe 2"],
  "merged_shopping_list": {{
    "dairy": [{{"item": "string", "total_quantity": "string"}}],
    "produce": [{{"item": "string", "total_quantity": "string"}}],
    "pantry": [{{"item": "string", "total_quantity": "string"}}],
    "bakery": [{{"item": "string", "total_quantity": "string"}}],
    "meat": [{{"item": "string", "total_quantity": "string"}}],
    "spices": [{{"item": "string", "total_quantity": "string"}}],
    "other": [{{"item": "string", "total_quantity": "string"}}]
  }},
  "estimated_prep_time_total": "string",
  "tips": ["tip 1", "tip 2"]
}}
"""

MEAL_PLAN_PROMPT = PromptTemplate(
    input_variables=["recipes_json"],
    template=MEAL_PLAN_TEMPLATE
)
