"""
Background worker: fetch BGG credits for games in MongoDB and update game documents.
"""

import time
from datetime import datetime

from etl.api.job_store import is_cancel_requested, update_job
from etl.extraction.bgg_credits_scraper import BGGCreditsScraper
from etl.load import DataLoader
from etl.lib.mongodb import COLLECTIONS
from etl.logger import get_logger
from etl.transform import build_game_update_from_credits

logger = get_logger(__name__)

DEFAULT_BATCH_SIZE = 10
DEFAULT_DELAY = 5.0
DEFAULT_TIMEOUT = 30


def run_credits_job(
    job_id: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
    delay_between_requests: float = DEFAULT_DELAY,
    timeout: int = DEFAULT_TIMEOUT,
    cookie: str | None = None,
    force_update: bool = False,
) -> None:
    """
    Run credits extraction: query games missing credits (or all if force_update),
    scrape BGG, update game documents in MongoDB.
    """
    loader = DataLoader()
    try:
        loader.connect()
        update_job(job_id, status="running", started_at=datetime.utcnow())

        collection = loader.mongo.get_collection(COLLECTIONS["GAMES"])
        if force_update:
            query = {"bggId": {"$exists": True, "$ne": None}}
        else:
            query = {
                "bggId": {"$exists": True, "$ne": None},
                "$or": [
                    {"designers": {"$exists": False}},
                    {"designers": {"$size": 0}},
                ],
            }
        cursor = collection.find(query, {"_id": 1, "bggId": 1})
        games = list(cursor)
        total = len(games)
        update_job(job_id, progress={"processed": 0, "total": total, "errors": 0})
        logger.info("Credits job %s: starting, games_to_process=%s", job_id, total)

        if total == 0:
            update_job(
                job_id,
                status="completed",
                finished_at=datetime.utcnow(),
                progress={"processed": 0, "total": 0, "errors": 0},
            )
            return

        processed = 0
        errors = 0
        with BGGCreditsScraper(
            delay_between_requests=delay_between_requests,
            timeout=timeout,
            cookie=cookie,
        ) as scraper:
            for i, game in enumerate(games):
                if is_cancel_requested(job_id):
                    logger.info("Credits job %s cancelled by user", job_id)
                    update_job(
                        job_id,
                        status="cancelled",
                        finished_at=datetime.utcnow(),
                        progress={
                            "processed": processed,
                            "total": total,
                            "errors": errors,
                        },
                    )
                    return
                bgg_id = game.get("bggId")
                if bgg_id is None:
                    continue
                try:
                    credits_data = scraper.scrape_credits(bgg_id=str(bgg_id))
                    if credits_data:
                        update_doc = build_game_update_from_credits(credits_data)
                        collection.update_one(
                            {"_id": game["_id"]},
                            {"$set": update_doc},
                        )
                    processed += 1
                except Exception as e:
                    logger.exception("Credits scrape failed for bggId=%s: %s", bgg_id, e)
                    errors += 1
                update_job(
                    job_id,
                    progress={
                        "processed": processed,
                        "total": total,
                        "errors": errors,
                    },
                )
                if (i + 1) % batch_size == 0:
                    time.sleep(delay_between_requests)

        update_job(
            job_id,
            status="completed",
            finished_at=datetime.utcnow(),
            progress={"processed": processed, "total": total, "errors": errors},
        )
        logger.info("Credits job %s: completed, processed=%s, errors=%s", job_id, processed, errors)
    except Exception as e:
        logger.exception("Credits job %s failed: %s", job_id, e)
        update_job(
            job_id,
            status="failed",
            finished_at=datetime.utcnow(),
            error=str(e),
        )
    finally:
        loader.disconnect()
