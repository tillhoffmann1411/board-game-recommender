"""
ETL Pipeline Main Module

Orchestrates the full ETL pipeline: Extract, Transform, Load.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to Python path for imports
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pandas as pd
from bson import ObjectId

from etl.config import get_config, Config
from etl.logger import setup_logging, get_logger
from etl.transform import (
    transform_game_from_csv,
    transform_shadow_user,
    transform_rating,
)
from etl.load import DataLoader
from etl.read_csv import read_csv_files
from etl.merge_csv_data import merge_csv_data

logger = get_logger(__name__)


class ETLPipeline:
    """Main ETL pipeline orchestrator."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the pipeline.

        Args:
            config: Configuration instance. If None, loads from environment.
        """
        self.config = config or get_config()
        self.loader = DataLoader()

        # ID mappings
        self.game_id_map: dict[int, ObjectId] = {}  # bggId -> ObjectId
        self.username_id_map: dict[str, ObjectId] = {}  # username -> ObjectId

    def run(
        self,
        data_dir: Optional[Path] = None,
        pattern: Optional[str] = None,
        files_to_import: Optional[list[str]] = None,
    ) -> dict:
        """
        Run the full ETL pipeline.

        Args:
            data_dir: Override data directory from config
            pattern: Override CSV file pattern from config
            files_to_import: Override files to import from config

        Returns:
            Statistics about the pipeline run
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)

        # Use config or overrides
        csv_data_dir = data_dir or self.config.csv_import.data_dir
        csv_pattern = pattern or self.config.csv_import.file_pattern
        csv_files = files_to_import or self.config.csv_import.files_to_import

        # Resolve relative paths
        if csv_data_dir and not csv_data_dir.is_absolute():
            csv_data_dir = Path(csv_data_dir).resolve()

        logger.info(f"CSV data directory: {csv_data_dir}")
        logger.info(f"CSV file pattern: {csv_pattern}")
        logger.info(f"Files to import: {csv_files}")

        # Check data directory
        if not csv_data_dir.exists():
            logger.error(f"Data directory not found: {csv_data_dir}")
            return {"error": "Data directory not found"}

        try:
            # Initialize database
            logger.info("Initializing database...")
            self.loader.initialize()

            # Read CSV files
            logger.info("Reading CSV files...")
            csv_data = read_csv_files(csv_data_dir, csv_pattern, csv_files)

            # Merge CSV data
            logger.info("Merging CSV data...")
            merged_games_df, shadow_profiles_dict, ratings_df = merge_csv_data(csv_data)

            # Transform and load games
            logger.info("Transforming and loading games...")
            games_loaded = self._process_games(merged_games_df)

            # Create and load shadow profiles
            logger.info("Creating and loading shadow profiles...")
            users_loaded = self._process_shadow_profiles(shadow_profiles_dict)

            # Transform and load ratings
            ratings_loaded = 0
            if ratings_df is not None and not ratings_df.empty:
                logger.info("Transforming and loading ratings...")
                ratings_loaded = self._process_ratings(ratings_df)
            else:
                logger.info("No ratings data to process")

            # Get final stats
            stats = self.loader.get_stats()

            elapsed = datetime.now() - start_time
            logger.info("=" * 60)
            logger.info(f"ETL Pipeline completed in {elapsed.total_seconds():.1f}s")
            logger.info(f"Final stats: {stats}")
            logger.info("=" * 60)

            return {
                "games": games_loaded,
                "users": users_loaded,
                "ratings": ratings_loaded,
                "elapsed_seconds": elapsed.total_seconds(),
            }

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            return {"error": str(e)}

        finally:
            self.loader.disconnect()

    def _process_games(self, games_df: pd.DataFrame) -> int:
        """
        Transform and load games from merged DataFrame.

        Args:
            games_df: Merged games DataFrame

        Returns:
            Number of games loaded
        """
        games = []
        errors = 0

        for idx, row in games_df.iterrows():
            try:
                raw = row.to_dict()
                game = transform_game_from_csv(raw)

                # Only include games with valid names and BGG IDs
                if game["name"] and game["bggId"]:
                    # Store BGG ID mapping for rating references
                    self.game_id_map[game["bggId"]] = game["_id"]
                    games.append(game)
                else:
                    errors += 1
                    if errors <= 5:
                        logger.warning(f"Skipping row {idx}: missing name or bggId")
            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"Error processing game row {idx}: {e}")

        if errors > 5:
            logger.warning(f"Total game errors: {errors}")

        logger.info(f"Transformed {len(games)} games")
        return self.loader.load_games(games, drop_existing=True)

    def _process_shadow_profiles(self, shadow_profiles_dict: dict[str, dict]) -> int:
        """
        Create and load shadow profile users.

        Args:
            shadow_profiles_dict: Dictionary mapping username to profile data

        Returns:
            Number of users loaded
        """
        users = []

        for username, profile_data in shadow_profiles_dict.items():
            try:
                user = transform_shadow_user(
                    username=username,
                    rating_count=profile_data.get("ratingCount", 0),
                    origin="bgg",
                )
                # Store username mapping for rating references
                self.username_id_map[username] = user["_id"]
                users.append(user)
            except Exception as e:
                logger.warning(f"Error creating shadow profile for {username}: {e}")

        logger.info(f"Created {len(users)} shadow profiles")
        return self.loader.load_users(users, drop_existing=True)

    def _process_ratings(self, ratings_df: pd.DataFrame) -> int:
        """
        Transform and load ratings from DataFrame.

        Args:
            ratings_df: Ratings DataFrame

        Returns:
            Number of ratings loaded
        """
        ratings = []
        skipped = 0

        for idx, row in ratings_df.iterrows():
            try:
                bgg_id = row.get("bggId")
                username = str(row.get("username", "")).strip()
                rating_value = row.get("rating")

                # Skip if missing required fields
                if pd.isna(bgg_id) or not username or pd.isna(rating_value):
                    skipped += 1
                    continue

                bgg_id_int = int(bgg_id)

                # Find game and user IDs
                game_id = self.game_id_map.get(bgg_id_int)
                user_id = self.username_id_map.get(username)

                if not game_id:
                    skipped += 1
                    if skipped <= 10:
                        logger.debug(
                            f"Skipping rating: game bggId {bgg_id_int} not found"
                        )
                    continue

                if not user_id:
                    skipped += 1
                    if skipped <= 10:
                        logger.debug(f"Skipping rating: username {username} not found")
                    continue

                rating = transform_rating(
                    row.to_dict(),
                    user_id=user_id,
                    game_id=game_id,
                    origin="bgg",
                )
                ratings.append(rating)
            except Exception as e:
                skipped += 1
                if skipped <= 10:
                    logger.warning(f"Error processing rating row {idx}: {e}")

        if skipped > 10:
            logger.warning(f"Total skipped ratings: {skipped}")

        logger.info(f"Transformed {len(ratings)} ratings")
        return self.loader.load_ratings(ratings, drop_existing=True)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Board Game Recommender ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with default settings (from config/env)
    python pipeline.py

    # Override data directory
    python pipeline.py --data-dir ./etl/data

    # Override pattern and files
    python pipeline.py --pattern "_1_100" --files games ratings credits

    # Verbose logging
    python pipeline.py --log-level DEBUG
        """,
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Path to CSV data directory (default: from config)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        help="CSV file pattern suffix (default: from config)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        choices=["games", "ratings", "credits"],
        help="Files to import (default: from config)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        help="Directory for log files (default: ./logs)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(
        level=args.log_level,
        log_dir=args.log_dir,
        log_to_file=True,
    )

    # Run pipeline
    pipeline = ETLPipeline()
    result = pipeline.run(
        data_dir=args.data_dir,
        pattern=args.pattern,
        files_to_import=args.files,
    )

    if "error" in result:
        logger.error(f"Pipeline failed: {result['error']}")
        sys.exit(1)

    logger.info(f"Pipeline completed successfully: {result}")


if __name__ == "__main__":
    main()
