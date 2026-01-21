"""
BoardGameGeek Credits Scraper

Scraper for extracting detailed game information from BoardGameGeek credits pages.
Extracts mechanics, categories, designers, alternate names, image URLs, and gameplay info.

Usage:
    from extraction.bgg_credits_scraper import scrape_game_credits

    credits_data = scrape_game_credits(
        game_url="https://boardgamegeek.com/boardgame/397598/dune-imperium-uprising",
        cookie=None
    )
"""

import re
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests

from etl.logger import get_logger

logger = get_logger(__name__)


class BGGCreditsScraper:
    """
    Scraper for BoardGameGeek game credits pages.

    Extracts:
    - Mechanics (as list)
    - Categories (as list)
    - Designer(s)
    - Alternate names (as list)
    - Image URL
    - Gameplay information (players, playtime, age, complexity)
    """

    BASE_URL = "https://boardgamegeek.com"

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

    def scrape_credits(
        self, game_url: Optional[str] = None, bgg_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape credits data for a game using the BGG API.

        Args:
            game_url: Base URL of the game (e.g., https://boardgamegeek.com/boardgame/397598/dune-imperium-uprising)
                     If bgg_id is provided, this parameter is ignored.
            bgg_id: BGG ID of the game (e.g., "397598"). If provided, game_url is ignored.

        Returns:
            Dictionary with extracted credits data or None if scraping fails
        """
        # Use bgg_id directly if provided, otherwise extract from URL
        if bgg_id:
            bgg_id = str(bgg_id)
        elif game_url:
            # Extract BGG ID from URL
            # URL format: https://boardgamegeek.com/boardgame/<bggId>/<name>
            bgg_id_match = re.search(r"/boardgame/(\d+)", game_url)
            if not bgg_id_match:
                logger.error(f"✗ Could not extract BGG ID from URL: {game_url}")
                return None
            bgg_id = bgg_id_match.group(1)
        else:
            logger.error("✗ Either game_url or bgg_id must be provided")
            return None

        api_url = (
            f"https://api.geekdo.com/api/geekitems?objectid={bgg_id}&objecttype=thing"
        )
        logger.debug(f"🌐 Fetching credits data from API for BGG ID: {bgg_id}")

        try:
            response = self.session.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            geek_data = response.json()

            if not geek_data or "item" not in geek_data:
                logger.warning(
                    f"⚠ No item data found in API response for BGG ID {bgg_id}"
                )
                return None

            credits_data: Dict[str, Any] = {
                "mechanics": [],
                "categories": [],
                "designers": [],
                "alternateNames": [],
                "imageUrl": None,
                "gameplay": {},
            }

            # Extract mechanics from links.boardgamemechanic
            if (
                "links" in geek_data.get("item", {})
                and "boardgamemechanic" in geek_data["item"]["links"]
            ):
                mechanics = geek_data["item"]["links"]["boardgamemechanic"]
                credits_data["mechanics"] = [
                    m.get("name", "") for m in mechanics if m.get("name")
                ]
                logger.debug(f"  • Mechanics: {len(credits_data['mechanics'])} found")

            # Extract categories from links.boardgamecategory
            if (
                "links" in geek_data.get("item", {})
                and "boardgamecategory" in geek_data["item"]["links"]
            ):
                categories = geek_data["item"]["links"]["boardgamecategory"]
                credits_data["categories"] = [
                    c.get("name", "") for c in categories if c.get("name")
                ]
                logger.debug(f"  • Categories: {len(credits_data['categories'])} found")

            # Extract designers from links.boardgamedesigner
            if (
                "links" in geek_data.get("item", {})
                and "boardgamedesigner" in geek_data["item"]["links"]
            ):
                designers = geek_data["item"]["links"]["boardgamedesigner"]
                credits_data["designers"] = [
                    d.get("name", "") for d in designers if d.get("name")
                ]
                logger.debug(f"  • Designers: {len(credits_data['designers'])} found")

            # Extract alternate names from alternatenames
            if "alternatenames" in geek_data.get("item", {}):
                alternatenames = geek_data["item"]["alternatenames"]
                credits_data["alternateNames"] = [
                    a.get("name", "") for a in alternatenames if a.get("name")
                ]
                logger.debug(
                    f"  • Alternate names: {len(credits_data['alternateNames'])} found"
                )

            # Extract image URL
            if "imageurl" in geek_data.get("item", {}):
                img_url = geek_data["item"]["imageurl"]
                if img_url:
                    if not img_url.startswith("http"):
                        img_url = urljoin(self.BASE_URL, img_url)
                    credits_data["imageUrl"] = img_url
                    logger.debug(f"  • Image URL: {img_url}")

            # Extract gameplay information
            item = geek_data.get("item", {})

            # Number of players
            min_players = item.get("minplayers")
            max_players = item.get("maxplayers")
            if min_players and max_players:
                if min_players == max_players:
                    credits_data["gameplay"]["numberofplayers"] = str(min_players)
                else:
                    credits_data["gameplay"][
                        "numberofplayers"
                    ] = f"{min_players}–{max_players}"
            elif min_players:
                credits_data["gameplay"]["numberofplayers"] = str(min_players)
            elif max_players:
                credits_data["gameplay"]["numberofplayers"] = str(max_players)

            # Playtime
            min_playtime = item.get("minplaytime")
            max_playtime = item.get("maxplaytime")
            if min_playtime and max_playtime:
                if min_playtime == max_playtime:
                    credits_data["gameplay"]["playtime"] = str(min_playtime)
                else:
                    credits_data["gameplay"][
                        "playtime"
                    ] = f"{min_playtime}–{max_playtime}"
            elif min_playtime:
                credits_data["gameplay"]["playtime"] = str(min_playtime)
            elif max_playtime:
                credits_data["gameplay"]["playtime"] = str(max_playtime)

            # Age
            min_age = item.get("minage")
            if min_age:
                credits_data["gameplay"]["suggestedage"] = f"{min_age}+"

            # Complexity/Weight from polls
            if "polls" in item and "boardgameweight" in item["polls"]:
                weight_data = item["polls"]["boardgameweight"]
                if "averageweight" in weight_data:
                    credits_data["gameplay"]["complexity"] = str(
                        round(weight_data["averageweight"], 2)
                    )

            mechanics_count = len(credits_data.get("mechanics", []))
            categories_count = len(credits_data.get("categories", []))
            designers_count = len(credits_data.get("designers", []))

            logger.debug(
                f"✓ Successfully extracted credits: "
                f"{mechanics_count} mechanics, "
                f"{categories_count} categories, "
                f"{designers_count} designers"
            )
            return credits_data

        except requests.RequestException as e:
            logger.error(
                f"✗ HTTP error fetching credits data for BGG ID {bgg_id}: {e}",
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(
                f"✗ Error processing credits data for BGG ID {bgg_id}: {e}",
                exc_info=True,
            )
            import traceback

            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None


def scrape_game_credits(
    game_url: Optional[str] = None,
    bgg_id: Optional[str] = None,
    cookie: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to scrape game credits.

    Args:
        game_url: Base URL of the game. If bgg_id is provided, this parameter is ignored.
        bgg_id: BGG ID of the game. If provided, game_url is ignored.
        cookie: Optional Cookie header value for authenticated requests

    Returns:
        Dictionary with extracted credits data or None if scraping fails
    """
    with BGGCreditsScraper(cookie=cookie) as scraper:
        return scraper.scrape_credits(game_url=game_url, bgg_id=bgg_id)


if __name__ == "__main__":
    # Example usage
    import argparse
    from etl.logger import setup_logging

    parser = argparse.ArgumentParser(description="Scrape BoardGameGeek game credits")
    parser.add_argument(
        "game_url",
        type=str,
        help="Base URL of the game (e.g., https://boardgamegeek.com/boardgame/397598/dune-imperium-uprising)",
    )
    parser.add_argument(
        "--cookie",
        type=str,
        default=None,
        help="Cookie header value for authenticated requests",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    setup_logging(level=args.log_level)

    credits_data = scrape_game_credits(
        game_url=args.game_url,
        cookie=args.cookie,
    )

    if credits_data:
        import json

        print(json.dumps(credits_data, indent=2, ensure_ascii=False))
    else:
        print("Failed to scrape credits data")
