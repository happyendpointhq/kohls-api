"""Minimal client for the Kohl's API on RapidAPI.

Set RAPIDAPI_KEY in your environment (or in a .env file at the repo root).
"""

import json
import os
import re

import requests

HOST = "kohls-com.p.rapidapi.com"


def _load_dotenv():
    """Read RAPIDAPI_KEY from a .env in the current folder or the repo root, if present."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    for path in (".env", os.path.join(root, ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                key, sep, value = line.strip().partition("=")
                if sep and value and not key.startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def get(path, **params):
    """GET an endpoint and return the parsed JSON body.

    The endpoints do not share one envelope: search and categories wrap results in
    `payload`, reviews and Q&A in `response`, and the store locator returns its fields at
    the top level.
    """
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise SystemExit("Set RAPIDAPI_KEY first (see .env.example).")
    response = requests.get(
        f"https://{HOST}{path}",
        params={k: v for k, v in params.items() if v is not None},
        headers={"x-rapidapi-host": HOST, "x-rapidapi-key": key},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def current_price(product):
    """Return (regular, sale, label, sale_ends) for the price entry marked current.

    `prices` is a list of price windows. Each has a regular and a sale price as
    {minPrice, maxPrice} (maxPrice is null unless the product is a price range) and the
    window the sale price is shown for.
    """
    prices = product.get("prices") or []
    entry = next((p for p in prices if p.get("isCurrentPrice")), prices[0] if prices else None)
    if not entry:
        return None, None, None, None
    regular = (entry.get("regularPrice") or {}).get("minPrice")
    sale = (entry.get("salePrice") or {}).get("minPrice")
    return regular, sale, entry.get("priceLabel"), entry.get("displayEndDateTime")


def review_stats(response, filtered=False):
    """Rating statistics for the product in a /product-reviews response.

    ReviewStatistics covers every rating, including ratings left without text.
    FilteredReviewStatistics covers only the written reviews the endpoint returns.
    """
    products = (response.get("Includes") or {}).get("Products") or {}
    product = next(iter(products.values()), {})
    return product.get("FilteredReviewStatistics" if filtered else "ReviewStatistics") or {}


_STORE_JSON = re.compile(r"\{.*\}", re.S)


def parse_store(marker):
    """Store markers carry the address as JSON inside an HTML string (`info`)."""
    match = _STORE_JSON.search(marker.get("info") or "")
    store = json.loads(match.group(0)) if match else {}
    store["specialties"] = [s["name"] for s in marker.get("specialties") or []]
    return store
