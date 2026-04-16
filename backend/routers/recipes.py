"""
Recipe API routes.
Handles: extraction, history listing, detail fetch, meal planning, delete.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import (
    ExtractRequest,
    RecipeResponse,
    RecipeListItem,
    MealPlanRequest,
)
from services import crud
from services.scraper import scrape_url
from services.llm_service import extract_recipe_from_text, generate_meal_plan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["recipes"])


@router.post("/extract", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def extract_recipe(payload: ExtractRequest, db: Session = Depends(get_db)):
    """
    Main endpoint: accepts a recipe URL, scrapes it, sends to LLM,
    stores in DB, and returns the full structured recipe.
    
    If the URL was already processed, returns the cached result.
    """
    url = payload.url.strip()

    # Return cached result if URL already processed
    existing = crud.get_recipe_by_url(db, url)
    if existing:
        logger.info(f"Cache hit for URL: {url}")
        return existing

    # Step 1: Scrape the URL
    try:
        scraped_text = scrape_url(url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Step 2: Extract structured data via LLM
    try:
        recipe_data = extract_recipe_from_text(scraped_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Step 3: Persist to database
    recipe_data["url"] = url
    recipe_data["raw_scraped_text"] = scraped_text[:2000]  # Store first 2k chars for debug

    new_recipe = crud.create_recipe(db, recipe_data)
    logger.info(f"Recipe saved with id={new_recipe.id}: {new_recipe.title}")

    return new_recipe


@router.get("/recipes", response_model=List[RecipeListItem])
def list_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns all previously extracted recipes for the history tab.
    Lightweight response — only title, cuisine, difficulty, date.
    """
    return crud.get_all_recipes(db, skip=skip, limit=limit)


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Returns full recipe detail by ID (used for the Details modal)."""
    recipe = crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id={recipe_id} not found.")
    return recipe


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe from history."""
    deleted = crud.delete_recipe(db, recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Recipe with id={recipe_id} not found.")


@router.post("/meal-plan")
def create_meal_plan(payload: MealPlanRequest, db: Session = Depends(get_db)):
    """
    Meal Planner: takes 3-5 recipe IDs, generates a merged shopping list
    with consolidated ingredient quantities via LLM.
    """
    if not (2 <= len(payload.recipe_ids) <= 5):
        raise HTTPException(
            status_code=422,
            detail="Please select between 2 and 5 recipes for a meal plan."
        )

    recipes = crud.get_recipes_by_ids(db, payload.recipe_ids)
    if len(recipes) != len(payload.recipe_ids):
        found_ids = {r.id for r in recipes}
        missing = set(payload.recipe_ids) - found_ids
        raise HTTPException(status_code=404, detail=f"Recipes not found: {missing}")

    # Convert ORM objects to dicts for the LLM service
    recipe_dicts = [
        {
            "title": r.title,
            "ingredients": r.ingredients or [],
        }
        for r in recipes
    ]

    try:
        meal_plan = generate_meal_plan(recipe_dicts)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return meal_plan
