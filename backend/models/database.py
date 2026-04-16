"""
SQLAlchemy models for the Recipe Extractor app.
Uses SQLite for simplicity and portability.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")

# SQLite needs check_same_thread=False for FastAPI's async handling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Recipe(Base):
    """
    Stores all recipe data extracted from a blog URL.
    Ingredients, instructions, substitutions, etc. stored as JSON columns.
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, index=True, nullable=False)
    title = Column(String(512), nullable=True)
    cuisine = Column(String(128), nullable=True)
    prep_time = Column(String(64), nullable=True)
    cook_time = Column(String(64), nullable=True)
    total_time = Column(String(64), nullable=True)
    servings = Column(Integer, nullable=True)
    difficulty = Column(String(32), nullable=True)

    # Complex fields stored as JSON
    ingredients = Column(JSON, nullable=True)       # [{quantity, unit, item}]
    instructions = Column(JSON, nullable=True)      # [step1, step2, ...]
    nutrition_estimate = Column(JSON, nullable=True) # {calories, protein, carbs, fat}
    substitutions = Column(JSON, nullable=True)     # [str, ...]
    shopping_list = Column(JSON, nullable=True)     # {category: [items]}
    related_recipes = Column(JSON, nullable=True)   # [str, ...]

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_scraped_text = Column(Text, nullable=True)  # For debugging / re-processing


def get_db():
    """Dependency injector for FastAPI route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database. Called on startup."""
    Base.metadata.create_all(bind=engine)
