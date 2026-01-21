"""
BoardGameGeek Ratings Batch Scraper

Processes CSV files with game data and extracts ratings information for each game.
Handles batch processing with progress saving and graceful cancellation.

Usage:
    python -m etl.extraction.bgg_ratings_batch_scraper \
        --input data/test_bgg_games_1_100.csv \
        --output data/game_ratings.csv \
        --cookie "your-cookie-here"
"""

# Configuration
BATCH_SIZE = 10  # Number of games to process before saving progress
DELAY_BETWEEN_REQUESTS = 5.0  # Delay between rating page requests (seconds)
DEFAULT_TIMEOUT = 30  # Request timeout (seconds)
DEFAULT_MAX_PAGES = 30  # Default maximum pages per game

import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd
from tqdm import tqdm

from etl.logger import get_logger
from etl.extraction.bgg_ratings_scraper import BGGRatingsScraper

logger = get_logger(__name__)


def process_csv_ratings(
    input_csv: Path,
    output_csv: Path,
    cookie: Optional[str] = None,
    batch_size: int = BATCH_SIZE,
    delay_between_requests: float = DELAY_BETWEEN_REQUESTS,
    max_pages: int = DEFAULT_MAX_PAGES,
    start_from_row: int = 0,
) -> None:
    """
    Process a CSV file and extract ratings for each game.

    Args:
        input_csv: Path to input CSV file with game data
        output_csv: Path to output CSV file for ratings data
        cookie: Optional Cookie header value for authenticated requests
        batch_size: Number of games to process before saving progress
        delay_between_requests: Delay between rating page requests (seconds)
        max_pages: Maximum number of pages to scrape per game
        start_from_row: Row index to start from (for resuming)
    """
    input_path = Path(input_csv)
    output_path = Path(output_csv)

    if not input_path.exists():
        logger.error(f"Input CSV file not found: {input_path}")
        return

    # Read input CSV
    logger.info("=" * 80)
    logger.info(f"📂 Reading input CSV: {input_path}")
    try:
        df = pd.read_csv(input_path)
        logger.info(f"✓ Successfully loaded CSV with {len(df)} rows")
    except Exception as e:
        logger.error(f"✗ Failed to read input CSV: {e}")
        return

    # Check required columns
    required_columns = ["bggId"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"✗ Missing required columns in CSV: {missing_columns}")
        return

    # Filter out rows with missing bggId
    initial_count = len(df)
    df = df.dropna(subset=["bggId"])
    filtered_count = initial_count - len(df)
    if filtered_count > 0:
        logger.warning(f"⚠ Filtered out {filtered_count} rows with missing bggId")

    total_games = len(df)
    logger.info(f"📊 Total games to process: {total_games}")
    logger.info("=" * 80)

    # Load existing results if output file exists (for resuming)
    existing_bgg_ids = set()
    all_ratings_data = []
    if output_path.exists():
        try:
            existing_df = pd.read_csv(output_path)
            if "bggId" in existing_df.columns:
                existing_bgg_ids = set(existing_df["bggId"].astype(str))
                # Load existing ratings data
                for _, row in existing_df.iterrows():
                    rating_entry = {
                        "bggId": str(row["bggId"]),
                        "rating": row.get("rating"),
                        "rating_tstamp": row.get("rating_tstamp"),
                        "username": row.get("username"),
                        "isocountry": row.get("isocountry", ""),
                    }
                    # Preserve rating_count if it exists (for backward compatibility)
                    if "rating_count" in existing_df.columns:
                        rating_entry["rating_count"] = row.get("rating_count")
                    all_ratings_data.append(rating_entry)
                logger.info(
                    f"📋 Found {len(existing_bgg_ids)} unique games with existing ratings"
                )
                logger.info(f"🔄 Resuming from where we left off...")
        except Exception as e:
            logger.warning(f"Could not read existing output file: {e}")

    # Track collected data for progress saving
    collected_ratings: List[Dict[str, Any]] = []

    def save_progress(current_ratings: List[Dict[str, Any]]) -> None:
        """Save current progress to CSV file."""
        nonlocal collected_ratings
        collected_ratings = current_ratings

        if current_ratings:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_output = pd.DataFrame(current_ratings)
            df_output.to_csv(output_path, index=False, encoding="utf-8")
            logger.debug(
                f"💾 Progress saved: {len(current_ratings)} ratings to {output_path}"
            )

    try:
        with BGGRatingsScraper(
            delay_between_requests=delay_between_requests,
            timeout=DEFAULT_TIMEOUT,
            cookie=cookie,
        ) as scraper:
            processed_count = 0
            skipped_count = 0
            new_ratings_count = 0
            error_count = 0

            # Filter rows to process (skip before start_from_row and already processed)
            rows_to_process = []
            for idx, row in df.iterrows():
                if idx < start_from_row:
                    continue
                bgg_id = str(row["bggId"])
                if bgg_id in existing_bgg_ids:
                    skipped_count += 1
                    continue
                rows_to_process.append((idx, row))

            remaining_games = len(rows_to_process)
            logger.info(f"🎯 Games remaining to process: {remaining_games}")
            logger.info(f"⏭️  Games already processed (skipped): {skipped_count}")
            logger.info("=" * 80)
            logger.info("🚀 Starting scraping process...")
            logger.info("=" * 80)

            # Create progress bar
            with tqdm(
                total=remaining_games,
                desc="Scraping games",
                unit="game",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
            ) as pbar:
                for idx, row in rows_to_process:
                    bgg_id = str(row["bggId"])

                    # Update progress bar description with current game
                    pbar.set_postfix(
                        {
                            "BGG ID": bgg_id,
                            "Processed": processed_count,
                            "Skipped": skipped_count,
                            "Errors": error_count,
                            "Ratings": len(all_ratings_data),
                        }
                    )

                    try:
                        # Scrape ratings using bgg_id directly
                        logger.debug(
                            f"Processing game {idx + 1}/{total_games} "
                            f"(BGG ID: {bgg_id})"
                        )
                        ratings_data = scraper.scrape_ratings(
                            bgg_id=bgg_id, max_pages=max_pages
                        )

                        if ratings_data:
                            # Add all ratings to the list
                            all_ratings_data.extend(ratings_data)
                            processed_count += 1
                            new_ratings_count += len(ratings_data)

                            logger.debug(
                                f"✓ Extracted {len(ratings_data)} ratings for {bgg_id}"
                            )
                        else:
                            logger.warning(
                                f"⚠ No ratings extracted for BGG ID {bgg_id}"
                            )
                            processed_count += 1
                            error_count += 1

                        # Save progress every batch_size new games processed
                        if processed_count > 0 and processed_count % batch_size == 0:
                            save_progress(all_ratings_data)
                            percentage = (
                                (processed_count / remaining_games * 100)
                                if remaining_games > 0
                                else 0
                            )
                            logger.info(
                                f"📊 Progress Update: "
                                f"{processed_count}/{remaining_games} games processed ({percentage:.1f}%), "
                                f"{skipped_count} skipped, "
                                f"{error_count} errors, "
                                f"{len(all_ratings_data)} total ratings"
                            )

                        # Update progress bar
                        pbar.update(1)

                        # Delay between requests (for different games)
                        if idx < len(df) - 1:
                            time.sleep(delay_between_requests)

                    except KeyboardInterrupt:
                        logger.warning(f"\n⚠ Processing interrupted at row {idx + 1}")
                        raise
                    except Exception as e:
                        logger.error(f"✗ Error processing game {bgg_id}: {e}")
                        error_count += 1
                        processed_count += 1
                        pbar.update(1)
                        continue

            # Final save
            save_progress(all_ratings_data)
            logger.info("=" * 80)
            logger.info("✅ Scraping completed successfully!")
            logger.info(f"📈 Final Statistics:")
            logger.info(f"   • Processed: {processed_count} games")
            logger.info(f"   • Skipped: {skipped_count} games")
            logger.info(f"   • Errors: {error_count} games")
            logger.info(f"   • Total ratings: {len(all_ratings_data)}")
            logger.info(f"💾 Data saved to: {output_path}")
            logger.info("=" * 80)

    except KeyboardInterrupt:
        # Save collected data before exiting
        logger.warning("\n" + "=" * 80)
        logger.warning("⚠ Processing interrupted by user")
        logger.warning("=" * 80)

        if collected_ratings:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_output = pd.DataFrame(collected_ratings)
            df_output.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(
                f"💾 Saving {len(collected_ratings)} collected ratings before exit..."
            )
            logger.info(f"✓ Data saved to {output_path}")
        elif all_ratings_data:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_output = pd.DataFrame(all_ratings_data)
            df_output.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(
                f"💾 Saving {len(all_ratings_data)} collected ratings before exit..."
            )
            logger.info(f"✓ Data saved to {output_path}")
        else:
            logger.warning("⚠ No ratings collected before interruption.")

        logger.info("👋 Exiting...")
        logger.info("=" * 80)

        # Re-raise to exit with proper signal
        raise


if __name__ == "__main__":
    import argparse
    from etl.logger import setup_logging

    parser = argparse.ArgumentParser(
        description="Batch scrape BoardGameGeek game ratings from CSV"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input CSV file with game data (must have 'bggId' column)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output CSV file for ratings data",
    )
    parser.add_argument(
        "--cookie",
        type=str,
        default=None,
        help="Cookie header value for authenticated requests",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Number of games to process before saving progress (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DELAY_BETWEEN_REQUESTS,
        help=f"Delay between requests in seconds (default: {DELAY_BETWEEN_REQUESTS})",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Maximum pages per game (default: {DEFAULT_MAX_PAGES})",
    )
    parser.add_argument(
        "--start-from-row",
        type=int,
        default=0,
        help="Row index to start from (0-indexed, for resuming)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    setup_logging(level=args.log_level)

    try:
        process_csv_ratings(
            input_csv=args.input,
            output_csv=args.output,
            cookie=args.cookie,
            batch_size=args.batch_size,
            delay_between_requests=args.delay,
            max_pages=args.max_pages,
            start_from_row=args.start_from_row,
        )

        print("\nRatings extraction completed successfully!")

    except KeyboardInterrupt:
        # Already handled in process_csv_ratings, just exit gracefully
        print("\nProcessing cancelled by user.")
        exit(0)
