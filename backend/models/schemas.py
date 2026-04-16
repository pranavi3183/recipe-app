"""
Pydantic schemas for request validation and response serialization.
"""

from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class IngredientItem(BaseModel):
    quantity: str
    unit: str
    item: str


class NutritionEstimate(BaseModel):
    calories: Optional[int] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None


class RecipeBase(BaseModel):
    url: str
    title: Optional[str] = None
    cuisine: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    ingredients: Optional[List[Dict[str, str]]] = None
    instructions: Optional[List[str]] = None
    nutrition_estimate: Optional[Dict[str, Any]] = None
    substitutions: Optional[List[str]] = None
    shopping_list: Optional[Dict[str, List[str]]] = None
    related_recipes: Optional[List[str]] = None

    @field_validator("ingredients", mode="before")
    @classmethod
    def coerce_ingredient_none_values(cls, v):
        if isinstance(v, list):
            return [{k: (val if val is not None else "") for k, val in item.items()} if isinstance(item, dict) else item for item in v]
        return v

    @field_validator("instructions", "substitutions", "related_recipes", mode="before")
    @classmethod
    def coerce_string_list_none_values(cls, v):
        if isinstance(v, list):
            return [item if item is not None else "" for item in v]
        return v

    @field_validator("shopping_list", mode="before")
    @classmethod
    def coerce_shopping_list_none_values(cls, v):
        if isinstance(v, dict):
            return {k: (val if isinstance(val, list) else []) for k, val in v.items()}
        return v


class RecipeCreate(RecipeBase):
    raw_scraped_text: Optional[str] = None


class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeListItem(BaseModel):
    """Lightweight schema for the history table."""
    id: int
    url: str
    title: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractRequest(BaseModel):
    url: str


class MealPlanRequest(BaseModel):
    recipe_ids: List[int]
