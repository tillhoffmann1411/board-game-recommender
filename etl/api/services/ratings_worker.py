"""
Background worker: fetch BGG ratings for games in MongoDB, create shadow users, insert ratings.
"""

import time
from datetime import datetime

from bson import ObjectId

from etl.api.job_store import is_cancel_requested, update_job
from etl.extraction.bgg_ratings_scraper import BGGRatingsScraper
from etl.load import DataLoader
from etl.lib.mongodb import COLLECTIONS
from etl.logger import get_logger
from etl.transform import transform_rating, transform_shadow_user

logger = get_logger(__name__)

DEFAULT_BATCH_SIZE = 10
DEFAULT_DELAY = 5.0
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_PAGES = 30


def _get_or_create_user_id(loader: DataLoader, username: str) -> ObjectId | None:
    """Return userId for shadow_bgg_{username}; create user if missing."""
    from etl.utils import clean_string

    username_clean = clean_string(username) or ""
    if not username_clean:
        return None
    clerk_id = f"shadow_bgg_{username_clean}"
    users_coll = loader.mongo.get_collection(COLLECTIONS["USERS"])
    user = users_coll.find_one({"clerkId": clerk_id}, {"_id": 1})
    if user:
        return user["_id"]
    user_doc = transform_shadow_user(username=username_clean, rating_count=0, origin="bgg")
    users_coll.insert_one(user_doc)
    return user_doc["_id"]


def run_ratings_job(
    job_id: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
    delay_between_requests: float = DEFAULT_DELAY,
    max_pages: int = DEFAULT_MAX_PAGES,
    timeout: int = DEFAULT_TIMEOUT,
    cookie: str | None = None,
    force_update: bool = False,
) -> None:
    """
    Run ratings extraction: query games without ratings (or all if force_update),
    scrape BGG, upsert shadow users and insert ratings into MongoDB.
    """
    loader = DataLoader()
    try:
        loader.connect()
        update_job(job_id, status="running", started_at=datetime.utcnow())

        games_coll = loader.mongo.get_collection(COLLECTIONS["GAMES"])
        ratings_coll = loader.mongo.get_collection(COLLECTIONS["RATINGS"])

        if force_update:
            query = {"bggId": {"$exists": True, "$ne": None}}
        else:
            game_ids_with_ratings = set(ratings_coll.distinct("gameId"))
            query = {
                "bggId": {"$exists": True, "$ne": None},
                "_id": {"$nin": list(game_ids_with_ratings)},
            }
        cursor = games_coll.find(query, {"_id": 1, "bggId": 1})
        games = list(cursor)
        total = len(games)
        update_job(job_id, progress={"processed": 0, "total": total, "errors": 0, "ratings_inserted": 0})

        if total == 0:
            update_job(
                job_id,
                status="completed",
                finished_at=datetime.utcnow(),
                progress={"processed": 0, "total": 0, "errors": 0, "ratings_inserted": 0},
            )
            return

        processed = 0
        errors = 0
        ratings_inserted = 0
        with BGGRatingsScraper(
            delay_between_requests=delay_between_requests,
            timeout=timeout,
            cookie=cookie,
        ) as scraper:
            for i, game in enumerate(games):
                if is_cancel_requested(job_id):
                    logger.info("Ratings job %s cancelled by user", job_id)
                    update_job(
                        job_id,
                        status="cancelled",
                        finished_at=datetime.utcnow(),
                        progress={
                            "processed": processed,
                            "total": total,
                            "errors": errors,
                            "ratings_inserted": ratings_inserted,
                        },
                    )
                    return
                bgg_id = game.get("bggId")
                game_id = game.get("_id")
                if bgg_id is None or game_id is None:
                    continue
                try:
                    if force_update:
                        ratings_coll.delete_many({"gameId": game_id})
                    ratings_data = scraper.scrape_ratings(bgg_id=str(bgg_id), max_pages=max_pages)
                    if ratings_data:
                        to_insert = []
                        for raw in ratings_data:
                            username = raw.get("username")
                            if not username:
                                continue
                            user_id = _get_or_create_user_id(loader, username)
                            if user_id is None:
                                continue
                            rating_doc = transform_rating(
                                raw,
                                user_id=user_id,
                                game_id=game_id,
                                origin="bgg",
                            )
                            to_insert.append(rating_doc)
                        if to_insert:
                            try:
                                result = ratings_coll.insert_many(to_insert, ordered=False)
                                ratings_inserted += len(result.inserted_ids)
                            except Exception as bulk_err:
                                # Duplicate key etc.; partial insert may have occurred
                                details = getattr(bulk_err, "details", None)
                                n_inserted = (
                                    details.get("nInserted", 0)
                                    if isinstance(details, dict)
                                    else 0
                                )
                                if n_inserted:
                                    ratings_inserted += n_inserted
                                logger.warning("Ratings insert partial failure: %s", bulk_err)
                    processed += 1
                except Exception as e:
                    logger.exception("Ratings scrape failed for bggId=%s: %s", bgg_id, e)
                    errors += 1
                update_job(
                    job_id,
                    progress={
                        "processed": processed,
                        "total": total,
                        "errors": errors,
                        "ratings_inserted": ratings_inserted,
                    },
                )
                if (i + 1) % batch_size == 0:
                    time.sleep(delay_between_requests)

        update_job(
            job_id,
            status="completed",
            finished_at=datetime.utcnow(),
            progress={
                "processed": processed,
                "total": total,
                "errors": errors,
                "ratings_inserted": ratings_inserted,
            },
        )
    except Exception as e:
        logger.exception("Ratings job %s failed: %s", job_id, e)
        update_job(
            job_id,
            status="failed",
            finished_at=datetime.utcnow(),
            error=str(e),
        )
    finally:
        loader.disconnect()
