"""
CSV Data Merger Module

Merges CSV data from different sources into a unified structure for MongoDB.
"""

import json
import re
from typing import Optional

import pandas as pd
from bson import ObjectId

from etl.logger import get_logger
from etl.utils import clean_string, safe_int, safe_float

logger = get_logger(__name__)


def parse_json_array(value: str) -> list[str]:
    """
    Parse a JSON array string into a list of strings.

    Handles both proper JSON arrays and malformed strings.

    Args:
        value: JSON array string (e.g., '["Item1", "Item2"]')

    Returns:
        List of strings
    """
    if pd.isna(value) or not value:
        return []

    value_str = str(value).strip()
    if not value_str:
        return []

    # Try to parse as JSON first
    try:
        parsed = json.loads(value_str)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if item]
        return []
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: try to extract quoted strings
    # Matches strings like: "Item1", "Item2"
    matches = re.findall(r'"([^"]+)"', value_str)
    if matches:
        return [m.strip() for m in matches if m.strip()]

    # Last resort: split by comma if it looks like a list
    if "," in value_str:
        return [item.strip() for item in value_str.split(",") if item.strip()]

    return []


def parse_player_range(value: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse player range string (e.g., "2–4", "1-4", "2+") into min/max.

    Args:
        value: Player range string

    Returns:
        Tuple of (min_players, max_players)
    """
    if pd.isna(value) or not value:
        return None, None

    value_str = str(value).strip()
    if not value_str:
        return None, None

    # Handle ranges like "2–4", "2-4", "1-6"
    range_match = re.match(r"(\d+)[–-](\d+)", value_str)
    if range_match:
        return safe_int(range_match.group(1)), safe_int(range_match.group(2))

    # Handle single number with + (e.g., "2+")
    plus_match = re.match(r"(\d+)\+", value_str)
    if plus_match:
        min_val = safe_int(plus_match.group(1))
        return min_val, None

    # Handle single number
    single_match = re.match(r"(\d+)", value_str)
    if single_match:
        val = safe_int(single_match.group(1))
        return val, val

    return None, None


def parse_playtime_range(value: str) -> tuple[Optional[int], Optional[int]]:
    """
    Parse playtime range string (e.g., "60–120", "30-60") into min/max minutes.

    Args:
        value: Playtime range string

    Returns:
        Tuple of (min_playtime, max_playtime) in minutes
    """
    if pd.isna(value) or not value:
        return None, None

    value_str = str(value).strip()
    if not value_str:
        return None, None

    # Handle ranges like "60–120", "30-60"
    range_match = re.match(r"(\d+)[–-](\d+)", value_str)
    if range_match:
        return safe_int(range_match.group(1)), safe_int(range_match.group(2))

    # Handle single number
    single_match = re.match(r"(\d+)", value_str)
    if single_match:
        val = safe_int(single_match.group(1))
        return val, val

    return None, None


def parse_age(value: str) -> Optional[int]:
    """
    Parse age string (e.g., "14+", "13+") into integer.

    Args:
        value: Age string

    Returns:
        Minimum age or None
    """
    if pd.isna(value) or not value:
        return None

    value_str = str(value).strip()
    if not value_str:
        return None

    # Handle "14+", "13+" format
    age_match = re.match(r"(\d+)\+", value_str)
    if age_match:
        return safe_int(age_match.group(1))

    # Handle plain number
    age_match = re.match(r"(\d+)", value_str)
    if age_match:
        return safe_int(age_match.group(1))

    return None


def merge_game_data(
    games_df: pd.DataFrame, credits_df: Optional[pd.DataFrame]
) -> pd.DataFrame:
    """
    Merge game data from games and credits DataFrames.

    Args:
        games_df: DataFrame with basic game info (required)
        credits_df: DataFrame with credits/metadata (optional)

    Returns:
        Merged DataFrame with all game data
    """
    logger.info("Merging game data...")

    # Start with games dataframe
    merged = games_df.copy()

    if credits_df is None or credits_df.empty:
        logger.info("No credits data to merge")
        return merged

    # Merge on bggId
    merged = merged.merge(
        credits_df,
        on="bggId",
        how="left",
        suffixes=("", "_credits"),
    )

    logger.info(f"Merged {len(merged)} games with credits data")
    return merged


def extract_shadow_profiles(ratings_df: Optional[pd.DataFrame]) -> dict[str, dict]:
    """
    Extract unique usernames from ratings and create shadow profile mappings.

    Args:
        ratings_df: DataFrame with ratings data (optional)

    Returns:
        Dictionary mapping username to user document data
    """
    if ratings_df is None or ratings_df.empty:
        logger.info("No ratings data, skipping shadow profile extraction")
        return {}

    logger.info("Extracting shadow profiles from ratings...")

    # Group by username to count ratings
    user_stats = (
        ratings_df.groupby("username")
        .agg({"rating": "count", "bggId": "nunique"})
        .reset_index()
    )
    user_stats.columns = ["username", "ratingCount", "uniqueGames"]

    shadow_profiles = {}
    for _, row in user_stats.iterrows():
        username = str(row["username"]).strip()
        if not username:
            continue

        shadow_profiles[username] = {
            "username": username,
            "ratingCount": int(row["ratingCount"]),
            "uniqueGames": int(row["uniqueGames"]),
        }

    logger.info(f"Extracted {len(shadow_profiles)} shadow profiles")
    return shadow_profiles


def prepare_categories_mechanics(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse and normalize categories/mechanics from merged DataFrame.

    Args:
        merged_df: Merged game DataFrame

    Returns:
        DataFrame with normalized categories and mechanics arrays
    """
    logger.info("Preparing categories and mechanics...")

    # Parse mechanics from JSON array
    if "mechanics" in merged_df.columns:
        merged_df["mechanics"] = merged_df["mechanics"].apply(parse_json_array)
    else:
        merged_df["mechanics"] = [[]] * len(merged_df)

    # Parse categories from JSON array
    if "categories" in merged_df.columns:
        merged_df["categories"] = merged_df["categories"].apply(parse_json_array)
    else:
        merged_df["categories"] = [[]] * len(merged_df)

    # Parse designers from JSON array
    if "designers" in merged_df.columns:
        merged_df["designers"] = merged_df["designers"].apply(parse_json_array)
    else:
        merged_df["designers"] = [[]] * len(merged_df)

    # Parse gameplay info
    if "gameplay_numberofplayers" in merged_df.columns:
        player_ranges = merged_df["gameplay_numberofplayers"].apply(parse_player_range)
        merged_df["minPlayers"] = [r[0] for r in player_ranges]
        merged_df["maxPlayers"] = [r[1] for r in player_ranges]
    elif "minPlayers" not in merged_df.columns:
        merged_df["minPlayers"] = None
        merged_df["maxPlayers"] = None

    if "gameplay_playtime" in merged_df.columns:
        playtime_ranges = merged_df["gameplay_playtime"].apply(parse_playtime_range)
        merged_df["minPlaytime"] = [r[0] for r in playtime_ranges]
        merged_df["maxPlaytime"] = [r[1] for r in playtime_ranges]
    elif "minPlaytime" not in merged_df.columns:
        merged_df["minPlaytime"] = None
        merged_df["maxPlaytime"] = None

    if "gameplay_suggestedage" in merged_df.columns:
        merged_df["minAge"] = merged_df["gameplay_suggestedage"].apply(parse_age)
    elif "minAge" not in merged_df.columns:
        merged_df["minAge"] = None

    logger.info("Categories and mechanics prepared")
    return merged_df


def merge_csv_data(
    csv_data: dict[str, Optional[pd.DataFrame]],
) -> tuple[pd.DataFrame, dict[str, dict], Optional[pd.DataFrame]]:
    """
    Merge all CSV data into unified structure.

    Args:
        csv_data: Dictionary of file types to DataFrames

    Returns:
        Tuple of (merged_games_df, shadow_profiles_dict, ratings_df)
    """
    logger.info("=" * 60)
    logger.info("Merging CSV data")
    logger.info("=" * 60)

    # Get games (required)
    games_df = csv_data.get("games")
    if games_df is None or games_df.empty:
        raise ValueError("Games data is required but not found")

    # Get credits (optional)
    credits_df = csv_data.get("credits")

    # Merge games with credits
    merged_games = merge_game_data(games_df, credits_df)

    # Prepare categories/mechanics
    merged_games = prepare_categories_mechanics(merged_games)

    # Extract shadow profiles from ratings
    ratings_df = csv_data.get("ratings")
    shadow_profiles = extract_shadow_profiles(ratings_df)

    logger.info("=" * 60)
    logger.info("CSV data merge complete")
    logger.info(f"Games: {len(merged_games)}")
    logger.info(f"Shadow profiles: {len(shadow_profiles)}")
    logger.info(f"Ratings: {len(ratings_df) if ratings_df is not None else 0}")
    logger.info("=" * 60)

    return merged_games, shadow_profiles, ratings_df
