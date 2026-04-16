"""
Web scraping service using BeautifulSoup.
Extracts clean text content from recipe blog pages.

Strategy (in order):
1. JSON-LD structured data (schema.org/Recipe) – present on virtually all
   major recipe sites even when the page body is JS-rendered.
2. Targeted CSS selectors for recipe-specific content blocks.
3. Full body text as last resort.
"""

import json
import requests
import cloudscraper
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

# Full browser-like headers to reduce bot detection
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Cache-Control": "max-age=0",
}

# Tags to strip from HTML before text extraction
UNWANTED_TAGS = [
    "script", "style", "nav", "footer", "header",
    "aside", "advertisement", "iframe", "noscript",
    "svg", "button", "form", "meta", "link"
]

# CSS classes often used by recipe sites for content areas
RECIPE_CONTENT_SELECTORS = [
    "[class*='recipe']",
    "[class*='Recipe']",
    "[id*='recipe']",
    "[class*='ingredients']",
    "[class*='instructions']",
    "[class*='directions']",
    "article",
    "main",
    ".entry-content",
    ".post-content",
    "#content",
]


def _extract_jsonld_recipe(soup: BeautifulSoup) -> str:
    """
    Looks for schema.org/Recipe inside <script type="application/ld+json"> blocks.
    Returns a flat text representation of the recipe data, or "" if not found.
    """
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        # Handle top-level object or @graph array
        nodes = data if isinstance(data, list) else data.get("@graph", [data])

        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_type = node.get("@type", "")
            # @type can be a string or a list
            types = node_type if isinstance(node_type, list) else [node_type]
            if "Recipe" not in types:
                continue

            parts: list[str] = []

            if node.get("name"):
                parts.append(f"Recipe: {node['name']}")
            if node.get("description"):
                parts.append(f"Description: {node['description']}")

            # Ingredients
            ingredients = node.get("recipeIngredient", [])
            if ingredients:
                parts.append("Ingredients: " + ", ".join(str(i) for i in ingredients))

            # Instructions – can be a list of HowToStep objects or plain strings
            instructions = node.get("recipeInstructions", [])
            if instructions:
                steps = []
                for step in instructions:
                    if isinstance(step, dict):
                        steps.append(step.get("text", ""))
                    else:
                        steps.append(str(step))
                parts.append("Instructions: " + " ".join(filter(None, steps)))

            # Extra metadata
            for field, label in [
                ("recipeYield", "Yield"),
                ("prepTime", "Prep time"),
                ("cookTime", "Cook time"),
                ("totalTime", "Total time"),
                ("recipeCuisine", "Cuisine"),
                ("recipeCategory", "Category"),
            ]:
                val = node.get(field)
                if val:
                    parts.append(f"{label}: {val}")

            if parts:
                logger.info("Extracted recipe from JSON-LD structured data")
                return " | ".join(parts)

    return ""


def scrape_url(url: str, timeout: int = 15) -> str:
    """
    Fetches a URL and returns cleaned text content.

    Strategy:
    1. JSON-LD structured data (schema.org/Recipe) – most reliable.
    2. Targeted CSS selectors for recipe content blocks.
    3. Full body text as last resort.

    Raises:
        ValueError: For invalid URLs, HTTP errors, or non-HTML content.
    """
    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    response = None

    # Attempt 1: cloudscraper – handles Cloudflare / JS-challenge sites (e.g. allrecipes)
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        response = scraper.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        logger.info("Fetched URL with cloudscraper")
        if response.status_code != 200:
            logger.warning("cloudscraper returned non-200 status: %s", response.status_code)
    except Exception as cs_err:
        logger.warning(f"cloudscraper failed ({cs_err}), retrying with requests")
        response = None

    # Attempt 2: plain requests with enhanced headers
    if response is None:
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            response = session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            logger.info("Fetched URL with requests fallback")
            if response.status_code != 200:
                logger.warning("requests returned non-200 status: %s", response.status_code)
        except requests.exceptions.Timeout:
            raise ValueError(f"Request timed out after {timeout}s for URL: {url}")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Could not connect to URL: {url}")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error {e.response.status_code} for URL: {url}")

    # Check content type
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        raise ValueError(f"URL did not return HTML content (got: {content_type})")

    soup = BeautifulSoup(response.text, "lxml")

    # If production fetches are blocked or non-HTML, optionally try a Playwright browser
    use_playwright = os.getenv("USE_PLAYWRIGHT", "false").lower() in ("1", "true", "yes")
    if use_playwright and (not response or response.status_code != 200 or "text/html" not in content_type):
        try:
            from playwright.sync_api import sync_playwright

            logger.info("Attempting Playwright fallback for URL: %s", url)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(user_agent=HEADERS.get("User-Agent"))
                page = context.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
                pw_content = page.content()
                browser.close()
                soup = BeautifulSoup(pw_content, "lxml")
                logger.info("Playwright fallback succeeded for URL: %s", url)
        except Exception as pw_err:
            logger.warning("Playwright fallback failed: %s", pw_err)

    # --- Strategy 1: JSON-LD structured data (most reliable for recipe sites) ---
    extracted_text = _extract_jsonld_recipe(soup)

    # --- Strategy 2: targeted CSS selectors ---
    if not extracted_text:
        # Remove noisy tags before text extraction (do this AFTER JSON-LD extraction)
        for tag in soup.find_all(UNWANTED_TAGS):
            tag.decompose()

        for selector in RECIPE_CONTENT_SELECTORS:
            elements = soup.select(selector)
            if elements:
                combined = " ".join(el.get_text(separator=" ", strip=True) for el in elements)
                if len(combined) > 200:
                    extracted_text = combined
                    logger.info(f"Extracted content using selector: {selector}")
                    break

    # --- Strategy 3: full body text ---
    if not extracted_text:
        if not soup.find_all(UNWANTED_TAGS):  # already stripped above
            body = soup.find("body")
        else:
            for tag in soup.find_all(UNWANTED_TAGS):
                tag.decompose()
            body = soup.find("body")
        extracted_text = body.get_text(separator=" ", strip=True) if body else soup.get_text()
        logger.info("Fell back to full body text extraction")

    # Clean up whitespace
    cleaned = re.sub(r"\s+", " ", extracted_text).strip()

    if len(cleaned) < 100:
        raise ValueError("Page content is too short to be a valid recipe page.")

    # Truncate to ~6000 chars to stay within LLM token limits
    if len(cleaned) > 6000:
        cleaned = cleaned[:6000] + "...[truncated]"
        logger.info("Content truncated to 6000 chars for LLM")

    return cleaned


def validate_url_is_reachable(url: str) -> bool:
    """Quick check to see if a URL is reachable."""
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.head(url, headers=HEADERS, timeout=8, allow_redirects=True)
        return resp.status_code < 400
    except Exception:
        return False
