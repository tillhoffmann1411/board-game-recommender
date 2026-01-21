"""
BoardGameGeek Ratings Scraper

Scraper for extracting user ratings from BoardGameGeek API.
Extracts rating, rating_tstamp, username, and isocountry for each rating.

Usage:
    from extraction.bgg_ratings_scraper import scrape_game_ratings

    ratings = scrape_game_ratings(
        bgg_id="59294",
        max_pages=10,
        cookie=None
    )
"""

import time
from typing import Optional, List, Dict, Any

import requests

from etl.logger import get_logger

logger = get_logger(__name__)


class BGGRatingsScraper:
    """
    Scraper for BoardGameGeek game ratings using API.

    Extracts:
    - Rating (number)
    - Rating timestamp
    - Username
    - ISO country code
    - BGG ID
    """

    BASE_URL = "https://api.geekdo.com/api/collections"

    def __init__(
        self,
        delay_between_requests: float = 1.0,
        timeout: int = 30,
        cookie: Optional[str] = None,
    ):
        """
        Initialize the scraper.

        Args:
            delay_between_requests: Delay between HTTP requests (seconds)
            timeout: Request timeout (seconds)
            cookie: Optional Cookie header value for authenticated requests
        """
        self.delay_between_requests = delay_between_requests
        self.timeout = timeout
        self.session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if cookie:
            headers["Cookie"] = cookie
            logger.debug("🔐 Using authenticated requests with provided cookie")
        self.session.headers.update(headers)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()

    def scrape_ratings(self, bgg_id: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape ratings data for a game using the BGG API.

        Args:
            bgg_id: BGG ID of the game (e.g., "59294")
            max_pages: Maximum number of pages to scrape (default: 10)

        Returns:
            List of rating dictionaries, each containing:
            - bggId: BGG ID of the game
            - rating: Rating value (float/int)
            - rating_tstamp: Rating timestamp (string)
            - username: Username (string)
            - isocountry: ISO country code (string, can be empty)
            - rating_count: Sequential count of ratings for this game (starts at 1)
        """
        bgg_id = str(bgg_id)
        all_ratings = []
        rating_count = 0  # Counter for ratings per game
        EXPECTED_ITEMS_PER_PAGE = 50  # API returns 50 items per page by default

        logger.info(
            f"🌐 Starting to fetch ratings for BGG ID: {bgg_id} (max {max_pages} pages)"
        )

        for page_id in range(max_pages):
            # Add delay before each request (including the first one) to avoid rate limiting
            if page_id > 0:
                # Delay between page requests
                time.sleep(self.delay_between_requests)
            # Note: First page (page_id == 0) doesn't need a delay before it

            try:
                # API endpoint with pagination
                api_url = (
                    f"{self.BASE_URL}?ajax=1&objectid={bgg_id}&objecttype=thing"
                    f"&oneperuser=1&pageid={page_id}&require_review=true"
                    f"&showcount=100&sort=review_tstamp"
                )

                logger.info(
                    f"  📄 [{bgg_id}] Fetching page {page_id + 1}/{max_pages}..."
                )

                response = self.session.get(api_url, timeout=self.timeout)

                # Check for rate limiting before raising for status
                if response.status_code == 429:
                    retry_delay = (
                        self.delay_between_requests * 3
                    )  # Triple the delay for rate limiting
                    logger.warning(
                        f"⚠ [{bgg_id}] Rate limited (429) on page {page_id + 1}. "
                        f"Waiting {retry_delay:.1f}s before continuing..."
                    )
                    time.sleep(retry_delay)
                    # Retry the request
                    response = self.session.get(api_url, timeout=self.timeout)

                response.raise_for_status()
                data = response.json()

                # Check if we have items
                if not data or "items" not in data or not data["items"]:
                    logger.info(
                        f"  ✓ [{bgg_id}] No more items found on page {page_id + 1}, stopping pagination"
                    )
                    break

                items = data["items"]
                items_count = len(items)
                page_ratings = []

                # If we got 0 items or fewer than expected (and not the first page), this is likely the last page
                # Note: API returns 50 items per page by default, so we check if we got fewer than that
                is_last_page = items_count == 0 or (
                    items_count < EXPECTED_ITEMS_PER_PAGE and page_id > 0
                )

                for item in items:
                    rating_data: Dict[str, Any] = {
                        "bggId": bgg_id,
                        "rating": None,
                        "rating_tstamp": None,
                        "username": None,
                        "isocountry": "",
                    }

                    # Extract rating
                    if "rating" in item:
                        rating_value = item["rating"]
                        # Handle both int and float ratings
                        if rating_value is not None:
                            rating_data["rating"] = (
                                float(rating_value)
                                if isinstance(rating_value, (int, float))
                                else None
                            )

                    # Extract rating_tstamp
                    if "rating_tstamp" in item:
                        rating_tstamp = item["rating_tstamp"]
                        rating_data["rating_tstamp"] = (
                            str(rating_tstamp) if rating_tstamp is not None else None
                        )

                    # Extract user information
                    if "user" in item and item["user"]:
                        user = item["user"]
                        if "username" in user:
                            rating_data["username"] = (
                                str(user["username"]) if user["username"] else None
                            )
                        if "isocountry" in user:
                            rating_data["isocountry"] = (
                                str(user["isocountry"]) if user["isocountry"] else ""
                            )

                    # Only add if we have at least rating and username
                    if (
                        rating_data["rating"] is not None
                        and rating_data["username"] is not None
                    ):
                        rating_count += 1
                        rating_data["rating_count"] = rating_count
                        page_ratings.append(rating_data)
                    else:
                        logger.debug(
                            f"  ⚠ [{bgg_id}] Skipping item with missing rating or username"
                        )

                if page_ratings:
                    all_ratings.extend(page_ratings)
                    logger.info(
                        f"  ✓ [{bgg_id}] Page {page_id + 1}/{max_pages}: Extracted {len(page_ratings)} ratings "
                        f"(total so far: {rating_count} ratings)"
                    )

                    # If this was the last page (fewer items than expected), stop pagination
                    if is_last_page:
                        logger.info(
                            f"  ✓ [{bgg_id}] Last page detected (got {items_count} items, expected {EXPECTED_ITEMS_PER_PAGE}+), stopping pagination"
                        )
                        break
                else:
                    logger.info(
                        f"  ⚠ [{bgg_id}] No valid ratings found on page {page_id + 1}, stopping pagination"
                    )
                    break

            except requests.HTTPError as e:
                # Handle 429 Too Many Requests with longer delay (if not already handled above)
                if e.response is not None and e.response.status_code == 429:
                    retry_delay = (
                        self.delay_between_requests * 3
                    )  # Triple the delay for rate limiting
                    logger.warning(
                        f"⚠ [{bgg_id}] Rate limited (429) on page {page_id + 1}. "
                        f"Waiting {retry_delay:.1f}s before continuing..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        f"✗ [{bgg_id}] HTTP error on page {page_id + 1}: {e}",
                        exc_info=True,
                    )
                # Continue to next page instead of breaking
                continue
            except requests.RequestException as e:
                logger.error(
                    f"✗ [{bgg_id}] Request error on page {page_id + 1}: {e}",
                    exc_info=True,
                )
                # Continue to next page instead of breaking
                continue
            except Exception as e:
                logger.error(
                    f"✗ [{bgg_id}] Error processing page {page_id + 1}: {e}",
                    exc_info=True,
                )
                # Continue to next page instead of breaking
                continue

        logger.info(
            f"✓ [{bgg_id}] Completed: Extracted {len(all_ratings)} total ratings "
            f"(rating_count: 1-{rating_count})"
        )
        return all_ratings


def scrape_game_ratings(
    bgg_id: str,
    max_pages: int = 10,
    cookie: Optional[str] = None,
    delay_between_requests: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape game ratings.

    Args:
        bgg_id: BGG ID of the game
        max_pages: Maximum number of pages to scrape (default: 10)
        cookie: Optional Cookie header value for authenticated requests
        delay_between_requests: Delay between page requests (seconds)

    Returns:
        List of rating dictionaries
    """
    with BGGRatingsScraper(
        cookie=cookie, delay_between_requests=delay_between_requests
    ) as scraper:
        return scraper.scrape_ratings(bgg_id=bgg_id, max_pages=max_pages)


if __name__ == "__main__":
    # Example usage
    import argparse
    import json
    from etl.logger import setup_logging

    parser = argparse.ArgumentParser(description="Scrape BoardGameGeek game ratings")
    parser.add_argument(
        "bgg_id",
        type=str,
        help="BGG ID of the game (e.g., 59294)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum number of pages to scrape (default: 10)",
    )
    parser.add_argument(
        "--cookie",
        type=str,
        default=None,
        help="Cookie header value for authenticated requests",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between pages in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    setup_logging(level=args.log_level)

    ratings = scrape_game_ratings(
        bgg_id=args.bgg_id,
        max_pages=args.max_pages,
        cookie=args.cookie,
        delay_between_requests=args.delay,
    )

    print(json.dumps(ratings, indent=2, ensure_ascii=False))
    print(f"\nTotal ratings: {len(ratings)}")
