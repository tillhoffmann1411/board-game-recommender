"""
BGG Dataset Merger

Merges Kaggle BGG dataset with scraped BGG data, combining the best fields
from both sources into a unified schema.

Usage:
    python merge_datasets.py \
        --kaggle-csv ../data/bgg_dataset.csv \
        --scraped-csv data/test_bgg_games.csv \
        --output data/merged_bgg_games.csv
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from etl.logger import setup_logging, get_logger
from etl.utils import clean_string, safe_int, safe_float

logger = get_logger(__name__)


def parse_decimal(value) -> Optional[float]:
    """Parse decimal values that may use comma as separator."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Handle European format (comma as decimal separator)
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None


def parse_list(value: str, separator: str = ",") -> list[str]:
    """Parse comma-separated list values."""
    if pd.isna(value) or not value:
        return []
    return [item.strip() for item in str(value).split(separator) if item.strip()]


def merge_datasets(
    kaggle_csv: Path,
    scraped_csv: Path,
    output_csv: Path,
) -> dict:
    """
    Merge Kaggle and scraped BGG datasets.

    Args:
        kaggle_csv: Path to Kaggle dataset CSV (semicolon-separated)
        scraped_csv: Path to scraped dataset CSV (comma-separated)
        output_csv: Path to output merged CSV

    Returns:
        Statistics about the merge
    """
    logger.info("=" * 60)
    logger.info("Starting BGG Dataset Merge")
    logger.info("=" * 60)

    # Read Kaggle dataset
    logger.info(f"Reading Kaggle dataset from {kaggle_csv}...")
    if not kaggle_csv.exists():
        logger.error(f"Kaggle CSV not found: {kaggle_csv}")
        return {"error": f"Kaggle CSV not found: {kaggle_csv}"}

    kaggle_df = pd.read_csv(kaggle_csv, sep=";", encoding="utf-8-sig")
    logger.info(f"Loaded {len(kaggle_df)} games from Kaggle dataset")

    # Read scraped dataset
    logger.info(f"Reading scraped dataset from {scraped_csv}...")
    if not scraped_csv.exists():
        logger.error(f"Scraped CSV not found: {scraped_csv}")
        return {"error": f"Scraped CSV not found: {scraped_csv}"}

    scraped_df = pd.read_csv(scraped_csv, encoding="utf-8")
    logger.info(f"Loaded {len(scraped_df)} games from scraped dataset")

    # Normalize BGG IDs - filter out rows with missing IDs
    kaggle_df = kaggle_df.dropna(subset=["ID"])
    kaggle_df["bggId"] = kaggle_df["ID"].astype(int)

    scraped_df = scraped_df.dropna(subset=["bggId"])
    scraped_df["bggId"] = scraped_df["bggId"].astype(int)

    logger.info(
        f"After filtering missing IDs: {len(kaggle_df)} Kaggle games, {len(scraped_df)} scraped games"
    )

    # Create merged records
    logger.info("Merging datasets...")
    merged_records = []
    kaggle_processed = set()
    scraped_processed = set()

    # Process games that exist in both datasets
    kaggle_dict = {int(row["bggId"]): row for _, row in kaggle_df.iterrows()}
    scraped_dict = {int(row["bggId"]): row for _, row in scraped_df.iterrows()}

    common_ids = set(kaggle_dict.keys()) & set(scraped_dict.keys())
    logger.info(f"Found {len(common_ids)} games in both datasets")

    for bgg_id in common_ids:
        kaggle_row = kaggle_dict[bgg_id]
        scraped_row = scraped_dict[bgg_id]
        merged = merge_game_records(kaggle_row, scraped_row)
        merged_records.append(merged)
        kaggle_processed.add(bgg_id)
        scraped_processed.add(bgg_id)

    # Add games only in Kaggle dataset
    kaggle_only = set(kaggle_dict.keys()) - scraped_processed
    logger.info(f"Adding {len(kaggle_only)} games only in Kaggle dataset")
    for bgg_id in kaggle_only:
        kaggle_row = kaggle_dict[bgg_id]
        merged = merge_game_records(kaggle_row, None)
        merged_records.append(merged)

    # Add games only in scraped dataset
    scraped_only = set(scraped_dict.keys()) - kaggle_processed
    logger.info(f"Adding {len(scraped_only)} games only in scraped dataset")
    for bgg_id in scraped_only:
        scraped_row = scraped_dict[bgg_id]
        merged = merge_game_records(None, scraped_row)
        merged_records.append(merged)

    # Create merged DataFrame
    merged_df = pd.DataFrame(merged_records)
    logger.info(f"Created merged dataset with {len(merged_df)} games")

    # Ensure output directory exists
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    # Write merged CSV
    logger.info(f"Writing merged dataset to {output_csv}...")
    merged_df.to_csv(output_csv, index=False, encoding="utf-8")
    logger.info(f"Successfully wrote {len(merged_df)} games to {output_csv}")

    return {
        "total_games": len(merged_df),
        "common_games": len(common_ids),
        "kaggle_only": len(kaggle_only),
        "scraped_only": len(scraped_only),
        "output_file": str(output_csv),
    }


def merge_game_records(
    kaggle_row: Optional[pd.Series],
    scraped_row: Optional[pd.Series],
) -> dict:
    """
    Merge a single game record from both sources.

    Smart merge strategy:
    - From Scraped: description, thumbnailUrl, officialUrl, bggRank
    - From Kaggle: mechanics, categories, complexity, player counts, playtime, minAge
    - Best available: name, yearPublished, ratings

    Args:
        kaggle_row: Kaggle dataset row (or None)
        scraped_row: Scraped dataset row (or None)

    Returns:
        Merged game record dictionary
    """
    merged = {}

    # BGG ID (required)
    if kaggle_row is not None:
        merged["bggId"] = int(kaggle_row["ID"])
    elif scraped_row is not None:
        merged["bggId"] = int(scraped_row["bggId"])
    else:
        raise ValueError("At least one row must be provided")

    # Name (prefer scraped, fallback Kaggle)
    if scraped_row is not None and pd.notna(scraped_row.get("name")):
        merged["name"] = clean_string(scraped_row["name"])
    elif kaggle_row is not None and pd.notna(kaggle_row.get("Name")):
        merged["name"] = clean_string(kaggle_row["Name"])
    else:
        merged["name"] = None

    # Year Published (prefer scraped, fallback Kaggle)
    if scraped_row is not None and pd.notna(scraped_row.get("yearPublished")):
        year = safe_int(scraped_row["yearPublished"])
        merged["yearPublished"] = year
    elif kaggle_row is not None and pd.notna(kaggle_row.get("Year Published")):
        merged["yearPublished"] = safe_int(kaggle_row["Year Published"])
    else:
        merged["yearPublished"] = None

    # Player counts (from Kaggle)
    if kaggle_row is not None:
        merged["minPlayers"] = safe_int(kaggle_row.get("Min Players"))
        merged["maxPlayers"] = safe_int(kaggle_row.get("Max Players"))
    else:
        merged["minPlayers"] = None
        merged["maxPlayers"] = None

    # Playtime (from Kaggle)
    if kaggle_row is not None and pd.notna(kaggle_row.get("Play Time")):
        playtime = safe_int(kaggle_row["Play Time"])
        merged["minPlaytime"] = playtime
        merged["maxPlaytime"] = playtime
    else:
        merged["minPlaytime"] = None
        merged["maxPlaytime"] = None

    # Min Age (from Kaggle)
    if kaggle_row is not None:
        merged["minAge"] = safe_int(kaggle_row.get("Min Age"))
    else:
        merged["minAge"] = None

    # Complexity (from Kaggle)
    if kaggle_row is not None:
        merged["complexity"] = parse_decimal(kaggle_row.get("Complexity Average"))
    else:
        merged["complexity"] = None

    # Description (from Scraped)
    if scraped_row is not None and pd.notna(scraped_row.get("description")):
        merged["description"] = clean_string(scraped_row["description"])
    else:
        merged["description"] = None

    # Thumbnail URL (from Scraped)
    if scraped_row is not None and pd.notna(scraped_row.get("thumbnailUrl")):
        merged["thumbnailUrl"] = clean_string(scraped_row["thumbnailUrl"])
    else:
        merged["thumbnailUrl"] = None

    # Official URL (from Scraped detailUrl)
    if scraped_row is not None and pd.notna(scraped_row.get("detailUrl")):
        merged["officialUrl"] = clean_string(scraped_row["detailUrl"])
    else:
        merged["officialUrl"] = None

    # BGG Rank (from Scraped rank, fallback Kaggle)
    if scraped_row is not None and pd.notna(scraped_row.get("rank")):
        merged["bggRank"] = safe_int(scraped_row["rank"])
    elif kaggle_row is not None:
        merged["bggRank"] = safe_int(kaggle_row.get("BGG Rank"))
    else:
        merged["bggRank"] = None

    # Ratings (prefer scraped, fallback Kaggle)
    rating_avg = None
    rating_count = None

    if scraped_row is not None:
        # Try scraped avgRating first
        if pd.notna(scraped_row.get("avgRating")):
            rating_avg = safe_float(scraped_row["avgRating"])
        # Fallback to geekRating
        elif pd.notna(scraped_row.get("geekRating")):
            rating_avg = safe_float(scraped_row["geekRating"])
        # Count from scraped
        if pd.notna(scraped_row.get("numVoters")):
            rating_count = safe_int(scraped_row["numVoters"])

    if rating_avg is None and kaggle_row is not None:
        rating_avg = parse_decimal(kaggle_row.get("Rating Average"))
        rating_count = safe_int(kaggle_row.get("Users Rated"))

    merged["ratingAverage"] = rating_avg
    merged["ratingCount"] = rating_count

    # Mechanics (from Kaggle, comma-separated string)
    if kaggle_row is not None and pd.notna(kaggle_row.get("Mechanics")):
        mechanics_list = parse_list(kaggle_row["Mechanics"], separator=",")
        merged["mechanics"] = ",".join(mechanics_list) if mechanics_list else None
    else:
        merged["mechanics"] = None

    # Categories (from Kaggle Domains, comma-separated string)
    if kaggle_row is not None and pd.notna(kaggle_row.get("Domains")):
        categories_list = parse_list(kaggle_row["Domains"], separator=",")
        merged["categories"] = ",".join(categories_list) if categories_list else None
    else:
        merged["categories"] = None

    return merged


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Merge Kaggle and scraped BGG datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage
    python merge_datasets.py \\
        --kaggle-csv ../data/bgg_dataset.csv \\
        --scraped-csv data/test_bgg_games.csv \\
        --output data/merged_bgg_games.csv
        """,
    )
    parser.add_argument(
        "--kaggle-csv",
        type=Path,
        required=True,
        help="Path to Kaggle BGG dataset CSV (semicolon-separated)",
    )
    parser.add_argument(
        "--scraped-csv",
        type=Path,
        required=True,
        help="Path to scraped BGG dataset CSV (comma-separated)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output merged CSV file",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level, log_to_file=False)

    # Run merge
    result = merge_datasets(
        kaggle_csv=args.kaggle_csv,
        scraped_csv=args.scraped_csv,
        output_csv=args.output,
    )

    if "error" in result:
        logger.error(f"Merge failed: {result['error']}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Merge completed successfully")
    logger.info(f"Total games: {result['total_games']}")
    logger.info(f"Common games: {result['common_games']}")
    logger.info(f"Kaggle-only games: {result['kaggle_only']}")
    logger.info(f"Scraped-only games: {result['scraped_only']}")
    logger.info(f"Output file: {result['output_file']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
