"""
BoardGameGeek Credits Batch Scraper

Processes CSV files with game data and extracts credits information for each game.
Handles batch processing with progress saving and graceful cancellation.

Usage:
    python -m etl.extraction.bgg_credits_batch_scraper \
        --input data/test_bgg_games_1_100.csv \
        --output data/game_credits.csv \
        --cookie "your-cookie-here"
"""

# Configuration
BATCH_SIZE = 10  # Number of games to process before saving progress
DELAY_BETWEEN_REQUESTS = 5.0  # Delay between credit page requests (seconds)
DEFAULT_TIMEOUT = 30  # Request timeout (seconds)

import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any

import pandas as pd
from tqdm import tqdm

from etl.logger import get_logger
from etl.extraction.bgg_credits_scraper import BGGCreditsScraper

logger = get_logger(__name__)


def process_csv_credits(
    input_csv: Path,
    output_csv: Path,
    cookie: Optional[str] = None,
    batch_size: int = BATCH_SIZE,
    delay_between_requests: float = DELAY_BETWEEN_REQUESTS,
    start_from_row: int = 0,
) -> None:
    """
    Process a CSV file and extract credits for each game.

    Args:
        input_csv: Path to input CSV file with game data
        output_csv: Path to output CSV file for credits data
        cookie: Optional Cookie header value for authenticated requests
        batch_size: Number of games to process before saving progress
        delay_between_requests: Delay between credit page requests (seconds)
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
    required_columns = ["detailUrl", "bggId"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"✗ Missing required columns in CSV: {missing_columns}")
        return

    # Filter out rows with missing detailUrl or bggId
    initial_count = len(df)
    df = df.dropna(subset=["detailUrl", "bggId"])
    filtered_count = initial_count - len(df)
    if filtered_count > 0:
        logger.warning(
            f"⚠ Filtered out {filtered_count} rows with missing detailUrl or bggId"
        )

    total_games = len(df)
    logger.info(f"📊 Total games to process: {total_games}")
    logger.info("=" * 80)

    # Load existing results if output file exists (for resuming)
    existing_bgg_ids = set()
    all_credits_data = []
    if output_path.exists():
        try:
            existing_df = pd.read_csv(output_path)
            if "bggId" in existing_df.columns:
                existing_bgg_ids = set(existing_df["bggId"].astype(str))
                # Convert existing CSV data back to nested format for processing
                # We'll need to parse JSON strings back to lists
                for _, row in existing_df.iterrows():
                    try:
                        credits_entry = {
                            "bggId": str(row["bggId"]),
                            "mechanics": (
                                json.loads(row.get("mechanics", "[]"))
                                if pd.notna(row.get("mechanics"))
                                and row.get("mechanics")
                                else []
                            ),
                            "categories": (
                                json.loads(row.get("categories", "[]"))
                                if pd.notna(row.get("categories"))
                                and row.get("categories")
                                else []
                            ),
                            "designers": (
                                json.loads(row.get("designers", "[]"))
                                if pd.notna(row.get("designers"))
                                and row.get("designers")
                                else []
                            ),
                            "alternateNames": (
                                json.loads(row.get("alternateNames", "[]"))
                                if pd.notna(row.get("alternateNames"))
                                and row.get("alternateNames")
                                else []
                            ),
                            "imageUrl": (
                                row.get("imageUrl")
                                if pd.notna(row.get("imageUrl"))
                                else None
                            ),
                            "gameplay": {},
                        }
                        # Reconstruct gameplay dict from columns
                        gameplay_cols = [
                            col
                            for col in existing_df.columns
                            if col.startswith("gameplay_")
                        ]
                        for col in gameplay_cols:
                            key = col.replace("gameplay_", "")
                            if pd.notna(row.get(col)):
                                credits_entry["gameplay"][key] = row[col]
                        all_credits_data.append(credits_entry)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(
                            f"Error parsing existing entry for bggId {row.get('bggId')}: {e}"
                        )
                        continue
                logger.info(
                    f"📋 Found {len(existing_bgg_ids)} existing credits entries"
                )
                logger.info(f"🔄 Resuming from where we left off...")
        except Exception as e:
            logger.warning(f"Could not read existing output file: {e}")

    # Track collected data for progress saving
    collected_credits: List[Dict[str, Any]] = []

    def save_progress(current_credits: List[Dict[str, Any]]) -> None:
        """Save current progress to CSV file."""
        nonlocal collected_credits
        collected_credits = current_credits

        if current_credits:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Flatten nested structures for CSV
            flattened_credits = flatten_credits_for_csv(current_credits)
            df_output = pd.DataFrame(flattened_credits)
            df_output.to_csv(output_path, index=False, encoding="utf-8")
            logger.debug(
                f"💾 Progress saved: {len(current_credits)} credits to {output_path}"
            )

    try:
        with BGGCreditsScraper(
            delay_between_requests=delay_between_requests,
            timeout=DEFAULT_TIMEOUT,
            cookie=cookie,
        ) as scraper:
            processed_count = 0
            skipped_count = 0
            new_entries_count = 0
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
                detail_url = row["detailUrl"]
                if pd.isna(detail_url) or not detail_url:
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
                    detail_url = row["detailUrl"]

                    # Update progress bar description with current game
                    pbar.set_postfix(
                        {
                            "BGG ID": bgg_id,
                            "Processed": processed_count,
                            "Skipped": skipped_count,
                            "Errors": error_count,
                        }
                    )

                    try:
                        # Scrape credits using bgg_id directly
                        logger.debug(
                            f"Processing game {idx + 1}/{total_games} "
                            f"(BGG ID: {bgg_id}): {detail_url}"
                        )
                        credits_data = scraper.scrape_credits(bgg_id=bgg_id)

                        if credits_data:
                            # Add bggId to credits data
                            credits_data["bggId"] = bgg_id
                            all_credits_data.append(credits_data)
                            processed_count += 1
                            new_entries_count += 1

                            mechanics_count = len(credits_data.get("mechanics", []))
                            categories_count = len(credits_data.get("categories", []))
                            designers_count = len(credits_data.get("designers", []))

                            logger.debug(
                                f"✓ Extracted credits for {bgg_id}: "
                                f"{mechanics_count} mechanics, "
                                f"{categories_count} categories, "
                                f"{designers_count} designers"
                            )
                        else:
                            logger.warning(f"⚠ Failed to extract credits for {bgg_id}")
                            # Still add an entry with bggId but empty data
                            empty_credits = {
                                "bggId": bgg_id,
                                "mechanics": [],
                                "categories": [],
                                "designers": [],
                                "alternateNames": [],
                                "imageUrl": None,
                                "gameplay": {},
                            }
                            all_credits_data.append(empty_credits)
                            new_entries_count += 1
                            error_count += 1

                        # Save progress every batch_size new entries
                        if (
                            new_entries_count > 0
                            and new_entries_count % batch_size == 0
                        ):
                            save_progress(all_credits_data)
                            percentage = (
                                (processed_count / remaining_games * 100)
                                if remaining_games > 0
                                else 0
                            )
                            logger.info(
                                f"📊 Progress Update: "
                                f"{processed_count}/{remaining_games} processed ({percentage:.1f}%), "
                                f"{skipped_count} skipped, "
                                f"{error_count} errors, "
                                f"{len(all_credits_data)} total entries"
                            )

                        # Update progress bar
                        pbar.update(1)

                        # Delay between requests
                        if idx < len(df) - 1:
                            time.sleep(delay_between_requests)

                    except KeyboardInterrupt:
                        logger.warning(f"\n⚠ Processing interrupted at row {idx + 1}")
                        raise
                    except Exception as e:
                        logger.error(f"✗ Error processing game {bgg_id}: {e}")
                        error_count += 1
                        # Add empty entry to continue processing
                        empty_credits = {
                            "bggId": bgg_id,
                            "mechanics": [],
                            "categories": [],
                            "designers": [],
                            "alternateNames": [],
                            "imageUrl": None,
                            "gameplay": {},
                        }
                        all_credits_data.append(empty_credits)
                        new_entries_count += 1
                        pbar.update(1)
                        continue

            # Final save
            save_progress(all_credits_data)
            logger.info("=" * 80)
            logger.info("✅ Scraping completed successfully!")
            logger.info(f"📈 Final Statistics:")
            logger.info(f"   • Processed: {processed_count} games")
            logger.info(f"   • Skipped: {skipped_count} games")
            logger.info(f"   • Errors: {error_count} games")
            logger.info(f"   • Total entries: {len(all_credits_data)}")
            logger.info(f"💾 Data saved to: {output_path}")
            logger.info("=" * 80)

    except KeyboardInterrupt:
        # Save collected data before exiting
        logger.warning("\n" + "=" * 80)
        logger.warning("⚠ Processing interrupted by user")
        logger.warning("=" * 80)

        if collected_credits:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            flattened_credits = flatten_credits_for_csv(collected_credits)
            df_output = pd.DataFrame(flattened_credits)
            df_output.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(
                f"💾 Saving {len(collected_credits)} collected credits before exit..."
            )
            logger.info(f"✓ Data saved to {output_path}")
        elif all_credits_data:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            flattened_credits = flatten_credits_for_csv(all_credits_data)
            df_output = pd.DataFrame(flattened_credits)
            df_output.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(
                f"💾 Saving {len(all_credits_data)} collected credits before exit..."
            )
            logger.info(f"✓ Data saved to {output_path}")
        else:
            logger.warning("⚠ No credits collected before interruption.")

        logger.info("👋 Exiting...")
        logger.info("=" * 80)

        # Re-raise to exit with proper signal
        raise


def flatten_credits_for_csv(credits_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flatten credits data for CSV export.

    Args:
        credits_list: List of credits dictionaries

    Returns:
        List of flattened dictionaries suitable for CSV
    """
    flattened = []
    for credits_entry in credits_list:
        flat_row = {
            "bggId": credits_entry.get("bggId"),
            "mechanics": (
                json.dumps(credits_entry.get("mechanics", []), ensure_ascii=False)
                if credits_entry.get("mechanics")
                else None
            ),
            "categories": (
                json.dumps(credits_entry.get("categories", []), ensure_ascii=False)
                if credits_entry.get("categories")
                else None
            ),
            "designers": (
                json.dumps(credits_entry.get("designers", []), ensure_ascii=False)
                if credits_entry.get("designers")
                else None
            ),
            "alternateNames": (
                json.dumps(credits_entry.get("alternateNames", []), ensure_ascii=False)
                if credits_entry.get("alternateNames")
                else None
            ),
            "imageUrl": credits_entry.get("imageUrl"),
        }

        # Flatten gameplay dictionary
        gameplay = credits_entry.get("gameplay", {})
        for key, value in gameplay.items():
            flat_row[f"gameplay_{key}"] = value

        flattened.append(flat_row)

    return flattened


if __name__ == "__main__":
    import argparse
    from etl.logger import setup_logging

    parser = argparse.ArgumentParser(
        description="Batch scrape BoardGameGeek game credits from CSV"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input CSV file with game data (must have 'detailUrl' and 'bggId' columns)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output CSV file for credits data",
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
        process_csv_credits(
            input_csv=args.input,
            output_csv=args.output,
            cookie=args.cookie,
            batch_size=args.batch_size,
            delay_between_requests=args.delay,
            start_from_row=args.start_from_row,
        )

        print("\nCredits extraction completed successfully!")

    except KeyboardInterrupt:
        # Already handled in process_csv_credits, just exit gracefully
        print("\nProcessing cancelled by user.")
        exit(0)
