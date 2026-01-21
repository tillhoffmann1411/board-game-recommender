"""
CSV Reader Module

Finds and reads CSV files matching a pattern for ETL processing.
"""

import json
from pathlib import Path
from typing import Optional

import pandas as pd

from etl.logger import get_logger
from etl.utils import clean_string, safe_int, safe_float

logger = get_logger(__name__)


def find_csv_files(data_dir: Path, pattern: str, file_type: str) -> list[Path]:
    """
    Find CSV files matching the pattern and file type.

    Args:
        data_dir: Directory to search in
        pattern: Pattern suffix (e.g., "_1_100")
        file_type: Type of file to find ("games", "ratings", "credits")

    Returns:
        List of matching file paths, sorted
    """
    if not data_dir.exists():
        logger.warning(f"Data directory does not exist: {data_dir}")
        return []

    # Map file types to filename prefixes
    file_prefixes = {
        "games": "test_bgg_games",
        "ratings": "game_ratings",
        "credits": "game_credits",
    }

    prefix = file_prefixes.get(file_type)
    if not prefix:
        logger.warning(f"Unknown file type: {file_type}")
        return []

    # Find all files matching pattern
    # Pattern format: prefix + pattern + .csv (e.g., test_bgg_games_1_100.csv)
    pattern_str = f"{prefix}{pattern}.csv"
    files = sorted(data_dir.glob(pattern_str))

    if not files:
        logger.warning(f"No files found matching pattern '{pattern_str}' in {data_dir}")
    else:
        logger.info(
            f"Found {len(files)} file(s) for {file_type}: {[f.name for f in files]}"
        )

    return files


def read_games_csv(file_path: Path) -> pd.DataFrame:
    """
    Read and parse games CSV file.

    Args:
        file_path: Path to the games CSV file

    Returns:
        DataFrame with games data
    """
    logger.info(f"Reading games CSV: {file_path.name}")
    df = pd.read_csv(file_path, encoding="utf-8")

    # Ensure bggId is integer
    if "bggId" in df.columns:
        df["bggId"] = df["bggId"].astype("Int64")

    logger.info(f"Loaded {len(df)} games from {file_path.name}")
    return df


def read_ratings_csv(file_path: Path) -> pd.DataFrame:
    """
    Read and parse ratings CSV file.

    Args:
        file_path: Path to the ratings CSV file

    Returns:
        DataFrame with ratings data
    """
    logger.info(f"Reading ratings CSV: {file_path.name}")
    df = pd.read_csv(file_path, encoding="utf-8")

    # Ensure bggId is integer
    if "bggId" in df.columns:
        df["bggId"] = df["bggId"].astype("Int64")

    # Ensure rating is float
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    logger.info(f"Loaded {len(df)} ratings from {file_path.name}")
    return df


def read_credits_csv(file_path: Path) -> pd.DataFrame:
    """
    Read and parse credits CSV file.

    Args:
        file_path: Path to the credits CSV file

    Returns:
        DataFrame with credits data
    """
    logger.info(f"Reading credits CSV: {file_path.name}")
    df = pd.read_csv(file_path, encoding="utf-8")

    # Ensure bggId is integer
    if "bggId" in df.columns:
        df["bggId"] = df["bggId"].astype("Int64")

    logger.info(f"Loaded {len(df)} credits records from {file_path.name}")
    return df


def read_csv_files(
    data_dir: Path,
    pattern: str,
    files_to_import: list[str],
) -> dict[str, Optional[pd.DataFrame]]:
    """
    Read all CSV files matching the pattern.

    Args:
        data_dir: Directory containing CSV files
        pattern: Pattern suffix (e.g., "_1_100")
        files_to_import: List of file types to import ("games", "ratings", "credits")

    Returns:
        Dictionary mapping file types to DataFrames (None if file not found/not imported)
    """
    result: dict[str, Optional[pd.DataFrame]] = {}

    # Games are always required
    if "games" not in files_to_import:
        logger.warning("'games' not in files_to_import, but it's required. Adding it.")
        files_to_import = ["games"] + [f for f in files_to_import if f != "games"]

    for file_type in files_to_import:
        files = find_csv_files(data_dir, pattern, file_type)

        if not files:
            logger.warning(f"No files found for {file_type}, skipping")
            result[file_type] = None
            continue

        # Read all matching files and concatenate
        dfs = []
        for file_path in files:
            try:
                if file_type == "games":
                    df = read_games_csv(file_path)
                elif file_type == "ratings":
                    df = read_ratings_csv(file_path)
                elif file_type == "credits":
                    df = read_credits_csv(file_path)
                else:
                    logger.warning(f"Unknown file type: {file_type}")
                    result[file_type] = None
                    continue

                dfs.append(df)
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                continue

        if dfs:
            # Concatenate all dataframes
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(
                f"Combined {len(dfs)} file(s) for {file_type}: {len(combined_df)} total rows"
            )
            result[file_type] = combined_df
        else:
            result[file_type] = None

    return result
