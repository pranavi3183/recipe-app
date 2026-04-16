# Recipe Extractor & Meal Planner

A full-stack app that scrapes recipe blog URLs, extracts structured data using Google Gemini (via LangChain), and stores results in SQLite.

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | FastAPI + Uvicorn                 |
| Database  | SQLite (via SQLAlchemy)           |
| LLM       | Google Gemini 1.5 Flash (free)    |
| Scraping  | BeautifulSoup4 + requests         |
| Frontend  | React + Vite                      |

---

## Project Structure

```
recipe-app/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── .env                     # Environment variables
│   ├── requirements.txt
│   ├── models/
│   │   ├── database.py          # SQLAlchemy models + engine
│   │   └── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   └── recipes.py           # API route handlers
│   ├── services/
│   │   ├── scraper.py           # BeautifulSoup scraping
│   │   ├── llm_service.py       # Gemini LLM extraction
│   │   └── crud.py              # DB operations
│   ├── prompts/
│   │   └── templates.py         # LangChain prompt templates
│   └── sample_data/
│       ├── sample_urls.txt
│       └── grilled_cheese_output.json
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        ├── api/recipeApi.js
        ├── components/
        │   ├── RecipeDetail.jsx
        │   ├── RecipeModal.jsx
        │   └── MealPlanModal.jsx
        └── pages/
            ├── ExtractTab.jsx
            └── HistoryTab.jsx
```

---

## Setup Instructions

### 1. Get a Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API Key**
3. Copy the key

### 2. Backend Setup

```bash
# Navigate to backend
cd recipe-app/backend

# Create and activate virtual environment
python -m venv venv

# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key in .env
# Edit backend/.env and replace: your_gemini_api_key_here
# with your actual key, e.g.: GEMINI_API_KEY=AIzaSyABC123...

# Run the backend server
python main.py
# Server runs at: http://localhost:8000
# Swagger docs at: http://localhost:8000/docs
```

SQLite database file `recipes.db` is created automatically in the `backend/` folder on first run.

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd recipe-app/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# App runs at: http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint                | Description                              |
|--------|-------------------------|------------------------------------------|
| POST   | `/api/extract`          | Scrape URL and extract recipe via LLM    |
| GET    | `/api/recipes`          | List all saved recipes (history)         |
| GET    | `/api/recipes/{id}`     | Get full recipe by ID                    |
| DELETE | `/api/recipes/{id}`     | Delete a recipe                          |
| POST   | `/api/meal-plan`        | Generate merged meal plan (2–5 recipes)  |
| GET    | `/health`               | Health check                             |
| GET    | `/docs`                 | Swagger interactive API docs             |

### POST /api/extract

**Request:**
```json
{ "url": "https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/" }
```

**Response:** Full recipe JSON (see sample_data/grilled_cheese_output.json)

### POST /api/meal-plan

**Request:**
```json
{ "recipe_ids": [1, 2, 3] }
```

**Response:** Merged shopping list with consolidated quantities and meal prep tips.

---

## Testing Steps

1. Start both servers (backend on :8000, frontend on :5173)
2. Open http://localhost:5173
3. Paste a recipe URL (e.g. https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/)
4. Click **Extract Recipe** — wait ~10–20s for scraping + LLM
5. View the structured result (ingredients, nutrition, substitutions, shopping list)
6. Switch to **Saved Recipes** tab to see history
7. Click **Details** on any row to open the modal
8. Check 2–5 recipes and click **Generate Meal Plan** for a merged shopping list

### Testing with Swagger UI

Visit http://localhost:8000/docs and use the interactive API directly.

---

## Error Handling

The backend handles:
- Invalid / unreachable URLs → 422 with descriptive message
- Non-recipe pages (too short / no content) → 422
- LLM API key missing or invalid → 500 with clear message
- Duplicate URLs → returns cached result (no re-scraping)
- Network timeouts → 422 with timeout message

---

## Environment Variables (backend/.env)

```env
GEMINI_API_KEY=your_gemini_api_key_here   # Required
DATABASE_URL=sqlite:///./recipes.db        # SQLite path
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:5173
```
