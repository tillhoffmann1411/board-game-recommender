"""
Statistics and job list.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Query

from etl.api.job_store import list_jobs
from etl.api.schemas import StatsResponse
from etl.load import DataLoader
from etl.lib.mongodb import COLLECTIONS

router = APIRouter(tags=["stats"])


@router.get(
    "/stats",
    summary="Get statistics and jobs",
    description=(
        "Return database counts: total_games, games_with_credits (has mechanics/categories/designers), "
        "games_with_ratings (distinct games with at least one rating), games_with_all_data (credits and ratings). "
        "Also returns a list of jobs (extraction runs), optionally filtered by status."
    ),
    response_model=StatsResponse,
)
async def get_stats(
    jobs_limit: Annotated[int, Query(ge=1, le=100, description="Max jobs to return")] = 50,
    jobs_status: Annotated[Optional[str], Query(description="Filter jobs by status")] = None,
):
    loader = DataLoader()
    try:
        loader.connect()
        games_coll = loader.mongo.get_collection(COLLECTIONS["GAMES"])
        ratings_coll = loader.mongo.get_collection(COLLECTIONS["RATINGS"])

        total_games = games_coll.count_documents({})
        # Has credits: at least one of mechanics/categories/designers non-empty
        games_with_credits = games_coll.count_documents(
            {
                "$or": [
                    {"designers.0": {"$exists": True}},
                    {"mechanics.0": {"$exists": True}},
                    {"categories.0": {"$exists": True}},
                ]
            }
        )
        game_ids_with_ratings = set(ratings_coll.distinct("gameId"))
        games_with_ratings = len(game_ids_with_ratings)
        # Games with both credits and at least one rating
        games_with_credits_ids = set(
            doc["_id"]
            for doc in games_coll.find(
                {
                    "$or": [
                        {"designers.0": {"$exists": True}},
                        {"mechanics.0": {"$exists": True}},
                        {"categories.0": {"$exists": True}},
                    ]
                },
                {"_id": 1},
            )
        )
        games_with_all_data = len(games_with_credits_ids & game_ids_with_ratings)

        jobs = list_jobs(status_filter=jobs_status, limit=jobs_limit)
    finally:
        loader.disconnect()

    return {
        "total_games": total_games,
        "games_with_credits": games_with_credits,
        "games_with_ratings": games_with_ratings,
        "games_with_all_data": games_with_all_data,
        "jobs": jobs,
    }
