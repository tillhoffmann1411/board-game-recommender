"""
ETL Data Transformers

Transforms raw data into MongoDB-compatible documents.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId

from etl.logger import get_logger
from etl.utils import clean_string, safe_int, safe_float

logger = get_logger(__name__)


def transform_game(
    raw: dict,
    categories: list[str],
    mechanics: list[str],
    designers: list[dict],
    publishers: list[dict],
) -> dict:
    """
    Transform raw game data into MongoDB document format.

    Args:
        raw: Raw game data from ETL
        categories: List of category names
        mechanics: List of mechanic names
        designers: List of designer objects
        publishers: List of publisher objects

    Returns:
        MongoDB-compatible game document
    """
    now = datetime.utcnow()

    # Build rating objects
    bgg_rating = None
    if raw.get("bgg_average_user_rating") is not None:
        bgg_rating = {
            "average": safe_float(raw.get("bgg_average_user_rating")),
            "count": safe_int(raw.get("bgg_num_user_ratings")),
            "stddev": safe_float(raw.get("bgg_stddev")),
            "bayesAverage": safe_float(raw.get("bgg_bayes_average")),
        }

    return {
        "_id": ObjectId(),
        "bggId": safe_int(raw.get("bgg_game_id") or raw.get("bgg_id")),
        "name": clean_string(raw.get("name")),
        "description": clean_string(
            raw.get("game_description") or raw.get("description")
        ),
        "yearPublished": safe_int(raw.get("year_published")),
        "minPlayers": safe_int(raw.get("min_players")),
        "maxPlayers": safe_int(raw.get("max_players")),
        "minPlaytime": safe_int(raw.get("min_playtime")),
        "maxPlaytime": safe_int(raw.get("max_playtime")),
        "minAge": safe_int(raw.get("min_age")),
        "complexity": safe_float(
            raw.get("bgg_average_weight") or raw.get("complexity")
        ),
        "thumbnailUrl": clean_string(raw.get("thumbnail_url")),
        "imageUrl": clean_string(raw.get("image_url")),
        "categories": categories,
        "mechanics": mechanics,
        "designers": designers,
        "publishers": publishers,
        "bggRating": bgg_rating,
        "officialUrl": clean_string(raw.get("official_url")),
        "priceUs": safe_float(raw.get("bga_price_us_dollar") or raw.get("price_us")),
        "bggRank": safe_int(raw.get("bgg_rank")),
        "createdAt": now,
        "updatedAt": now,
    }


def transform_user(raw: dict, origin: str = "imported") -> dict:
    """
    Transform raw user data into MongoDB document format.

    Args:
        raw: Raw user data
        origin: User origin identifier

    Returns:
        MongoDB-compatible user document
    """
    now = datetime.utcnow()
    user_key = raw.get("user_key") or raw.get("id")

    return {
        "_id": ObjectId(),
        "clerkId": f"imported_{origin}_{user_key}",
        "username": clean_string(raw.get("user_name") or raw.get("username")),
        "displayName": None,
        "ratingCount": safe_int(raw.get("num_ratings") or raw.get("number_of_ratings"))
        or 0,
        "preferences": None,
        "createdAt": now,
        "updatedAt": now,
    }


def transform_rating(
    raw: dict,
    user_id: ObjectId,
    game_id: ObjectId,
    origin: str = "bgg",
) -> dict:
    """
    Transform raw rating data into MongoDB document format.

    Args:
        raw: Raw rating data
        user_id: MongoDB ObjectId for the user
        game_id: MongoDB ObjectId for the game
        origin: Rating origin (app, bgg)

    Returns:
        MongoDB-compatible rating document
    """
    now = datetime.utcnow()

    rating_origin = raw.get("user_origin") or raw.get("origin") or origin
    if rating_origin not in ("app", "bgg"):
        rating_origin = "bgg"

    return {
        "_id": ObjectId(),
        "userId": user_id,
        "gameId": game_id,
        "rating": safe_float(raw.get("rating")) or 0.0,
        "origin": rating_origin,
        "createdAt": now,
        "updatedAt": now,
    }


def transform_online_game(
    raw: dict,
    game_id: Optional[ObjectId] = None,
) -> dict:
    """
    Transform raw online game data into MongoDB document format.

    Args:
        raw: Raw online game data
        game_id: MongoDB ObjectId for the linked game (if matched)

    Returns:
        MongoDB-compatible online game document
    """
    now = datetime.utcnow()

    # Determine platform
    origin = (raw.get("origin") or "").lower()
    platform_map = {
        "tabletopia": "tabletopia",
        "boardgamearena": "board-game-arena",
        "board game arena": "board-game-arena",
        "yucata": "yucata",
    }
    platform = platform_map.get(origin, "other")

    return {
        "_id": ObjectId(),
        "gameId": game_id,
        "bggId": safe_int(raw.get("bgg_id")),
        "name": clean_string(raw.get("name")),
        "url": clean_string(raw.get("url")) or "",
        "platform": platform,
        "createdAt": now,
        "updatedAt": now,
    }


def transform_designer(raw: dict) -> dict:
    """Transform designer data for embedding in games."""
    return {
        "id": str(raw.get("designer_key") or raw.get("id")),
        "name": clean_string(raw.get("designer_name") or raw.get("name")),
        "url": clean_string(raw.get("designer_url") or raw.get("url")),
        "imageUrl": clean_string(raw.get("designer_image_url") or raw.get("image_url")),
    }


def transform_publisher(raw: dict) -> dict:
    """Transform publisher data for embedding in games."""
    return {
        "id": str(raw.get("publisher_key") or raw.get("id")),
        "name": clean_string(raw.get("publisher_name") or raw.get("name")),
        "url": clean_string(raw.get("publisher_url") or raw.get("url")),
        "imageUrl": clean_string(
            raw.get("publisher_image_url") or raw.get("image_url")
        ),
    }


def transform_similarity(
    game_id: ObjectId,
    similar_games: list[tuple[ObjectId, float]],
) -> dict:
    """
    Transform similarity data into MongoDB document format.

    Args:
        game_id: MongoDB ObjectId for the source game
        similar_games: List of (game_id, similarity_score) tuples

    Returns:
        MongoDB-compatible similarity document
    """
    return {
        "_id": ObjectId(),
        "gameId": game_id,
        "similarGames": [
            {"gameId": gid, "similarity": score} for gid, score in similar_games
        ],
        "computedAt": datetime.utcnow(),
    }


def transform_merged_game(raw: dict) -> dict:
    """
    Transform merged CSV row into MongoDB document format.

    This function handles the unified schema from merge_datasets.py which
    combines data from both Kaggle and scraped sources.

    Args:
        raw: Raw game data from merged CSV

    Returns:
        MongoDB-compatible game document
    """
    now = datetime.utcnow()

    # Parse mechanics and categories from comma-separated strings
    mechanics = []
    if raw.get("mechanics"):
        mechanics = [m.strip() for m in str(raw["mechanics"]).split(",") if m.strip()]

    categories = []
    if raw.get("categories"):
        categories = [c.strip() for c in str(raw["categories"]).split(",") if c.strip()]

    # Build BGG rating object
    bgg_rating = None
    rating_avg = safe_float(raw.get("ratingAverage"))
    rating_count = safe_int(raw.get("ratingCount"))

    if rating_avg is not None and rating_count is not None:
        bgg_rating = {
            "average": rating_avg,
            "count": rating_count,
        }

    return {
        "_id": ObjectId(),
        "bggId": safe_int(raw.get("bggId")),
        "name": clean_string(raw.get("name")),
        "description": clean_string(raw.get("description")),
        "yearPublished": safe_int(raw.get("yearPublished")),
        "minPlayers": safe_int(raw.get("minPlayers")),
        "maxPlayers": safe_int(raw.get("maxPlayers")),
        "minPlaytime": safe_int(raw.get("minPlaytime")),
        "maxPlaytime": safe_int(raw.get("maxPlaytime")),
        "minAge": safe_int(raw.get("minAge")),
        "complexity": safe_float(raw.get("complexity")),
        "thumbnailUrl": clean_string(raw.get("thumbnailUrl")),
        "imageUrl": None,  # Not in merged dataset
        "categories": categories,
        "mechanics": mechanics,
        "designers": [],  # Not in merged dataset
        "publishers": [],  # Not in merged dataset
        "bggRating": bgg_rating,
        "officialUrl": clean_string(raw.get("officialUrl")),
        "priceUs": None,
        "bggRank": safe_int(raw.get("bggRank")),
        "createdAt": now,
        "updatedAt": now,
    }


def transform_game_from_csv(raw: dict) -> dict:
    """
    Transform game data from merged CSV structure into MongoDB document format.

    This handles the structure from merge_csv_data.py which combines
    test_bgg_games and game_credits CSV files.

    Args:
        raw: Raw game data from merged CSV (pandas Series or dict)

    Returns:
        MongoDB-compatible game document
    """
    now = datetime.utcnow()

    # Handle pandas Series
    if hasattr(raw, "to_dict"):
        raw = raw.to_dict()

    # Extract categories and mechanics (already parsed as lists by merge_csv_data)
    categories = raw.get("categories", [])
    if not isinstance(categories, list):
        categories = []

    mechanics = raw.get("mechanics", [])
    if not isinstance(mechanics, list):
        mechanics = []

    # Extract designers (parsed as list)
    designers_list = raw.get("designers", [])
    if not isinstance(designers_list, list):
        designers_list = []

    # Transform designers to objects
    designers = []
    for designer_name in designers_list:
        if designer_name:
            designers.append({
                "id": clean_string(designer_name) or "",
                "name": clean_string(designer_name),
                "url": None,
                "imageUrl": None,
            })

    # Build BGG rating object from games CSV
    bgg_rating = None
    rating_avg = safe_float(raw.get("avgRating") or raw.get("geekRating"))
    rating_count = safe_int(raw.get("numVoters"))

    if rating_avg is not None and rating_count is not None:
        bgg_rating = {
            "average": rating_avg,
            "count": rating_count,
        }

    return {
        "_id": ObjectId(),
        "bggId": safe_int(raw.get("bggId")),
        "name": clean_string(raw.get("name")),
        "description": clean_string(raw.get("description")),
        "yearPublished": safe_int(raw.get("yearPublished")),
        "minPlayers": safe_int(raw.get("minPlayers")),
        "maxPlayers": safe_int(raw.get("maxPlayers")),
        "minPlaytime": safe_int(raw.get("minPlaytime")),
        "maxPlaytime": safe_int(raw.get("maxPlaytime")),
        "minAge": safe_int(raw.get("minAge")),
        "complexity": None,  # Not in CSV files
        "thumbnailUrl": clean_string(raw.get("thumbnailUrl")),
        "imageUrl": clean_string(raw.get("imageUrl")),
        "categories": categories,
        "mechanics": mechanics,
        "designers": designers,
        "publishers": [],  # Not in CSV files
        "bggRating": bgg_rating,
        "officialUrl": clean_string(raw.get("detailUrl")),
        "priceUs": None,
        "bggRank": safe_int(raw.get("rank")),
        "createdAt": now,
        "updatedAt": now,
    }


def transform_shadow_user(username: str, rating_count: int = 0, origin: str = "bgg") -> dict:
    """
    Transform shadow profile username into MongoDB user document format.

    Args:
        username: Username from ratings CSV
        rating_count: Number of ratings for this user
        origin: User origin identifier (default: "bgg")

    Returns:
        MongoDB-compatible user document
    """
    now = datetime.utcnow()
    username_clean = clean_string(username) or ""

    return {
        "_id": ObjectId(),
        "clerkId": f"shadow_{origin}_{username_clean}",
        "username": username_clean,
        "displayName": None,
        "ratingCount": rating_count,
        "preferences": None,
        "createdAt": now,
        "updatedAt": now,
    }
