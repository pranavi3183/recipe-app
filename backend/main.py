"""
Recipe Extractor & Meal Planner — FastAPI Application Entry Point
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.database import create_tables
from routers.recipes import router as recipe_router

load_dotenv()

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── App init ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Recipe Extractor & Meal Planner",
    description="Extracts structured recipe data from blog URLs using LLM.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────────────
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    logger.info("Creating database tables if they don't exist...")
    create_tables()
    logger.info("Database ready.")


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(recipe_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Recipe API is running"}


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true",
    )
