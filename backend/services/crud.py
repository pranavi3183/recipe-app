"""
CRUD operations for the Recipe model.
All DB interactions are isolated here for clean separation of concerns.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import Recipe
from models.schemas import RecipeCreate


def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
    """Fetch a single recipe by its primary key."""
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()


def get_recipe_by_url(db: Session, url: str) -> Optional[Recipe]:
    """Check if a recipe for this URL was already processed."""
    return db.query(Recipe).filter(Recipe.url == url).first()


def get_all_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
    """Fetch all recipes for the history tab, newest first."""
    return (
        db.query(Recipe)
        .order_by(Recipe.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_recipe(db: Session, data: dict) -> Recipe:
    """
    Insert a new recipe into the database.
    Accepts a plain dict (output of LLM extraction + URL).
    """
    recipe = Recipe(**data)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def get_recipes_by_ids(db: Session, ids: List[int]) -> List[Recipe]:
    """Batch fetch recipes by a list of IDs (used for meal planning)."""
    return db.query(Recipe).filter(Recipe.id.in_(ids)).all()


def delete_recipe(db: Session, recipe_id: int) -> bool:
    """Delete a recipe. Returns True if found and deleted."""
    recipe = get_recipe_by_id(db, recipe_id)
    if not recipe:
        return False
    db.delete(recipe)
    db.commit()
    return True
