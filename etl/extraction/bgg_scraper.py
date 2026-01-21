"""
BoardGameGeek Scraper

Automated scraper for extracting board game information from BoardGameGeek.com
using Beautiful Soup and requests.

Usage:
    from extraction.bgg_scraper import scrape_bgg_games

    games = scrape_bgg_games(max_pages=10, output_file="games.json")
"""

import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from etl.logger import get_logger

logger = get_logger(__name__)


class BGGScraper:
    """
    Scraper for BoardGameGeek.com board game listings.

    Extracts game information from the browse page including:
    - Game name and detail page link
    - Rank, ratings, and voter counts
    - Thumbnail images
    - Any other available metadata
    """

    BASE_URL = "https://boardgamegeek.com"
    BROWSE_URL = f"{BASE_URL}/browse/boardgame/page/"

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
        # Set user agent to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Add Cookie header if provided for authenticated requests
        if cookie:
            headers["Cookie"] = cookie
            logger.info("Using authenticated requests with provided cookie")
        self.session.headers.update(headers)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()

    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a page.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def get_total_pages(self) -> int:
        """
        Get the total number of pages from the first page.

        Returns:
            Total number of pages
        """
        url = f"{self.BROWSE_URL}1"
        soup = self._fetch_page(url)

        if not soup:
            logger.warning("Could not fetch first page. Assuming 1 page.")
            return 1

        try:
            # Find the "last page" link with title attribute
            last_page_link = soup.find("a", {"title": "last page"})

            if not last_page_link:
                logger.warning("Could not find last page link. Assuming 1 page.")
                return 1

            # Extract number from brackets in the link text (e.g., "Next » [1728]")
            text = last_page_link.get_text()
            match = re.search(r"\[(\d+)\]", text)
            if match:
                total_pages = int(match.group(1))
                logger.info(f"Found {total_pages} total pages")
                return total_pages
            else:
                logger.warning("Could not extract total pages from last page link")
                return 1

        except Exception as e:
            logger.warning(f"Error getting total pages: {e}. Assuming 1 page.")
            return 1

    def extract_game_from_row(self, row) -> Optional[Dict[str, Any]]:
        """
        Extract game information from a table row.

        Args:
            row: BeautifulSoup Tag representing a table row

        Returns:
            Dictionary with game information or None if extraction fails
        """
        try:
            game_data: Dict[str, Any] = {}

            # Get all table cells
            cells = row.find_all("td")
            if not cells:
                return None

            # Extract rank (first column)
            try:
                rank_text = cells[0].get_text(strip=True)
                game_data["rank"] = int(rank_text) if rank_text.isdigit() else None
            except (ValueError, IndexError):
                game_data["rank"] = None

            # Extract thumbnail image
            try:
                img = row.find("img")
                if img:
                    game_data["thumbnailUrl"] = img.get("src") or None
                    game_data["thumbnailAlt"] = img.get("alt") or None
                    # Make URL absolute if relative
                    if game_data["thumbnailUrl"] and not game_data[
                        "thumbnailUrl"
                    ].startswith("http"):
                        game_data["thumbnailUrl"] = urljoin(
                            self.BASE_URL, game_data["thumbnailUrl"]
                        )
                else:
                    game_data["thumbnailUrl"] = None
                    game_data["thumbnailAlt"] = None
            except Exception:
                game_data["thumbnailUrl"] = None
                game_data["thumbnailAlt"] = None

            # Extract game name (most important)
            try:
                # Find the td with class "collection_objectname" which contains the game name
                name_td = row.find("td", class_="collection_objectname")
                if not name_td:
                    logger.warning("Could not find collection_objectname td in row")
                    return None

                # Find the div with id starting with "results_objectname"
                name_div = name_td.find("div", id=re.compile(r"results_objectname\d+"))
                if not name_div:
                    logger.warning("Could not find results_objectname div in row")
                    return None

                game_name = name_div.get_text(strip=True)
                # remove published year from game name
                game_name = re.sub(r"\s*\(\d{4}\)\s*", "", game_name)
                game_data["name"] = game_name

            except Exception as e:
                logger.warning(f"Could not find game name in row: {e}")
                return None

            # Extract game detail link
            try:
                # Find the link within the name div
                name_td = row.find("td", class_="collection_objectname")
                if name_td:
                    name_div = name_td.find(
                        "div", id=re.compile(r"results_objectname\d+")
                    )
                    if name_div:
                        link_a = name_div.find("a", href=re.compile(r"/boardgame/\d+/"))
                        if link_a:
                            href = link_a.get("href")
                            # Make URL absolute if relative
                            if href and not href.startswith("http"):
                                href = urljoin(self.BASE_URL, href)
                            game_data["detailUrl"] = href
                            game_data["bggId"] = self._extract_bgg_id_from_url(href)
                        else:
                            game_data["detailUrl"] = None
                            game_data["bggId"] = None
                    else:
                        game_data["detailUrl"] = None
                        game_data["bggId"] = None
                else:
                    game_data["detailUrl"] = None
                    game_data["bggId"] = None

            except Exception as e:
                logger.warning(f"Could not find game link in row: {e}")
                game_data["detailUrl"] = None
                game_data["bggId"] = None

            # Extract year published (usually in parentheses after name)
            try:
                # Look for span with class "smallerfont dull" which contains the year
                name_td = row.find("td", class_="collection_objectname")
                if name_td:
                    name_div = name_td.find(
                        "div", id=re.compile(r"results_objectname\d+")
                    )
                    if name_div:
                        year_span = name_div.find("span", class_="smallerfont")
                        if year_span:
                            year_text = year_span.get_text()
                            year_match = re.search(r"\((\d{4})\)", year_text)
                            if year_match:
                                game_data["yearPublished"] = int(year_match.group(1))
                            else:
                                game_data["yearPublished"] = None
                        else:
                            # Try to find year in the div text
                            div_text = name_div.get_text()
                            year_match = re.search(r"\((\d{4})\)", div_text)
                            if year_match:
                                game_data["yearPublished"] = int(year_match.group(1))
                            else:
                                game_data["yearPublished"] = None
                    else:
                        game_data["yearPublished"] = None
                else:
                    game_data["yearPublished"] = None
            except (ValueError, AttributeError):
                game_data["yearPublished"] = None

            # Extract description (if available)
            try:
                description_tag = row.find("p")
                if description_tag:
                    description = description_tag.get_text(strip=True)
                    game_data["description"] = description if description else None
                else:
                    game_data["description"] = None
            except Exception:
                game_data["description"] = None

            # Extract ratings and voter counts from cells
            if len(cells) >= 5:
                try:
                    # Geek Rating (usually 3rd or 4th column)
                    geek_rating_text = cells[4].get_text(strip=True)
                    game_data["geekRating"] = (
                        float(geek_rating_text) if geek_rating_text else None
                    )
                except (ValueError, IndexError):
                    game_data["geekRating"] = None

                try:
                    # Average Rating (usually 4th or 5th column)
                    avg_rating_text = cells[5].get_text(strip=True)
                    game_data["avgRating"] = (
                        float(avg_rating_text) if avg_rating_text else None
                    )
                except (ValueError, IndexError):
                    game_data["avgRating"] = None

                try:
                    # Number of Voters (usually 5th or 6th column)
                    voters_text = cells[6].get_text(strip=True)
                    # Remove commas from numbers
                    voters_text = voters_text.replace(",", "")
                    game_data["numVoters"] = (
                        int(voters_text) if voters_text.isdigit() else None
                    )
                except (ValueError, IndexError):
                    game_data["numVoters"] = None
            else:
                game_data["geekRating"] = None
                game_data["avgRating"] = None
                game_data["numVoters"] = None

            # Store raw HTML for additional processing if needed
            game_data["_rawHtml"] = str(row)

            return game_data

        except Exception as e:
            logger.warning(f"Error extracting game from row: {e}")
            return None

    def _extract_bgg_id_from_url(self, url: str) -> Optional[int]:
        """
        Extract BGG game ID from a detail page URL.

        Args:
            url: Game detail page URL

        Returns:
            BGG game ID or None
        """
        try:
            # URLs are typically: /boardgame/224517/brass-birmingham
            match = re.search(r"/boardgame/(\d+)/", url)
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass
        return None

    def scrape_page(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Scrape a single page of board games.

        Args:
            page_num: Page number to scrape

        Returns:
            List of game dictionaries
        """
        url = f"{self.BROWSE_URL}{page_num}"
        logger.info(f"Scraping page {page_num}: {url}")

        soup = self._fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch page {page_num}")
            return []

        try:
            # Find the collection div
            collection_div = soup.find("div", id="collection")
            if not collection_div:
                logger.error(f"Could not find collection div on page {page_num}")
                return []

            # Find all table rows (skip header row)
            table = collection_div.find("table")
            if not table:
                logger.error(f"Could not find table on page {page_num}")
                return []

            rows = table.find_all("tr")

            games = []
            for row in rows:
                # Skip header row (usually contains "Title", "Geek Rating", etc.)
                if row.find("th"):
                    continue

                game = self.extract_game_from_row(row)
                if game:
                    game["page"] = page_num
                    games.append(game)

            logger.info(f"Extracted {len(games)} games from page {page_num}")
            return games

        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")
            return []

    def scrape_all(
        self,
        max_pages: Optional[int] = None,
        start_page: int = 1,
        delay_between_pages: float = 2.0,
        progress_callback: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scrape all pages or up to max_pages.

        Args:
            max_pages: Maximum number of pages to scrape (None for all)
            start_page: Page number to start from
            delay_between_pages: Delay between page requests (seconds)
            progress_callback: Optional callback function(games_list) called after each page

        Returns:
            List of all extracted games
        """
        all_games = []

        # Get total pages if not limited
        if max_pages is None:
            total_pages = self.get_total_pages()
            end_page = start_page + total_pages - 1
        else:
            end_page = start_page + max_pages - 1

        logger.info(f"Scraping pages {start_page} to {end_page}")

        try:
            for page_num in range(start_page, end_page + 1):
                try:
                    games = self.scrape_page(page_num)
                    all_games.extend(games)

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(all_games)

                    # Delay between pages to be respectful
                    if page_num < end_page:
                        time.sleep(delay_between_pages)

                except Exception as e:
                    logger.error(f"Failed to scrape page {page_num}: {e}")
                    continue

            logger.info(f"Total games extracted: {len(all_games)}")
            return all_games

        except KeyboardInterrupt:
            logger.warning(
                f"\nScraping interrupted by user. Collected {len(all_games)} games so far."
            )
            # Re-raise to allow caller to handle saving
            raise


def save_games_to_csv(games: List[Dict[str, Any]], output_file: Path) -> None:
    """
    Save scraped games to CSV file.

    Args:
        games: List of game dictionaries
        output_file: Path to save CSV file
    """
    if not games:
        logger.warning("No games to save")
        return

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Flatten nested structures and remove raw HTML for CSV
    csv_data = []
    for game in games:
        csv_row = {k: v for k, v in game.items() if k != "_rawHtml"}
        csv_data.append(csv_row)

    df = pd.DataFrame(csv_data)
    df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {len(games)} games to {output_file}")


def scrape_bgg_games(
    max_pages: Optional[int] = None,
    start_page: int = 1,
    output_file: Optional[Path] = None,
    output_format: str = "csv",
    delay_between_pages: float = 2.0,
    cookie: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape BGG games.

    Args:
        max_pages: Maximum number of pages to scrape (None for all)
        start_page: Page number to start from
        output_file: Optional path to save output (CSV or JSON)
        output_format: Output format - "csv" or "json" (default: "csv")
        delay_between_pages: Delay between page requests (seconds)
        cookie: Optional Cookie header value for authenticated requests

    Returns:
        List of extracted game dictionaries
    """
    # Use a list to track games across callback and exception handler
    collected_games: List[Dict[str, Any]] = []

    def save_progress(current_games: List[Dict[str, Any]]) -> None:
        """Save current progress to file if output_file is specified."""
        nonlocal collected_games
        collected_games = current_games  # Update the tracked list

        if output_file and current_games:
            output_file_path = Path(output_file)
            if output_format.lower() == "csv":
                save_games_to_csv(current_games, output_file_path)
            else:
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(current_games, f, indent=2, ensure_ascii=False)
                logger.info(
                    f"Progress saved: {len(current_games)} games to {output_file_path}"
                )

    try:
        with BGGScraper(delay_between_requests=1.0, cookie=cookie) as scraper:
            games = scraper.scrape_all(
                max_pages=max_pages,
                start_page=start_page,
                delay_between_pages=delay_between_pages,
                progress_callback=save_progress if output_file else None,
            )

            collected_games = games  # Update in case callback wasn't used

            # Save final results
            if output_file and games:
                output_file_path = Path(output_file)
                if output_format.lower() == "csv":
                    save_games_to_csv(games, output_file_path)
                else:
                    output_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file_path, "w", encoding="utf-8") as f:
                        json.dump(games, f, indent=2, ensure_ascii=False)
                    logger.info(f"Saved {len(games)} games to {output_file_path}")

            return games

    except KeyboardInterrupt:
        # Save collected data before exiting
        if collected_games and output_file:
            output_file_path = Path(output_file)
            logger.info(
                f"\nSaving {len(collected_games)} collected games before exit..."
            )
            if output_format.lower() == "csv":
                save_games_to_csv(collected_games, output_file_path)
            else:
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(collected_games, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved {len(collected_games)} games to {output_file_path}")
            logger.info(f"Data saved to {output_file_path}. Exiting...")
        elif collected_games:
            logger.warning(
                f"\nCollected {len(collected_games)} games but no output file specified. Data will be lost."
            )
        else:
            logger.warning("\nNo games collected before interruption.")

        # Re-raise to exit with proper signal
        raise


if __name__ == "__main__":
    # Example usage
    import argparse
    from etl.logger import setup_logging

    parser = argparse.ArgumentParser(description="Scrape BoardGameGeek games")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to scrape (default: all)",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Page number to start from (default: 1)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (CSV or JSON)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Delay between pages in seconds (default: 5.0 seconds defined by BGG)",
    )
    parser.add_argument(
        "--cookie",
        type=str,
        default=None,
        help="Cookie header value for authenticated requests (e.g., 'cc_cookie=...; bggusername=...; SessionID=...')",
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
        games = scrape_bgg_games(
            max_pages=args.max_pages,
            start_page=args.start_page,
            output_file=args.output,
            output_format=args.format,
            delay_between_pages=args.delay,
            cookie=args.cookie,
        )

        print(f"\nScraped {len(games)} games successfully!")

    except KeyboardInterrupt:
        # Already handled in scrape_bgg_games, just exit gracefully
        print("\nScraping cancelled by user.")
        exit(0)
