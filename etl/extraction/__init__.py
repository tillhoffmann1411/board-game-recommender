"""
Extraction Module

Web scraping and data extraction utilities for the ETL pipeline.
"""

from .bgg_scraper import BGGScraper, scrape_bgg_games
from .bgg_credits_scraper import BGGCreditsScraper, scrape_game_credits
from .bgg_ratings_scraper import BGGRatingsScraper, scrape_game_ratings
from .bgg_credits_batch_scraper import process_csv_credits

__all__ = [
    "BGGScraper",
    "scrape_bgg_games",
    "BGGCreditsScraper",
    "scrape_game_credits",
    "BGGRatingsScraper",
    "scrape_game_ratings",
    "process_csv_credits",
]
