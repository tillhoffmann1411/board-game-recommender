"""
Start credits and ratings extraction jobs.
"""

import threading
from typing import Annotated, Optional

from fastapi import APIRouter, Query

from etl.api.job_store import create_job
from etl.api.services.credits_worker import run_credits_job
from etl.api.services.ratings_worker import run_ratings_job

router = APIRouter(prefix="/extract", tags=["extract"])


@router.post(
    "/credits",
    summary="Start credits extraction",
    description="Start a background job that fetches BGG credits for games in MongoDB "
    "that are missing credits (or all games if force_update=true), then updates game documents.",
)
async def start_credits_extraction(
    batch_size: Annotated[int, Query(ge=1, le=100, description="Games per progress batch")] = 10,
    delay_between_requests: Annotated[float, Query(ge=0, le=60, description="Seconds between BGG requests")] = 5.0,
    timeout: Annotated[int, Query(ge=5, le=120, description="Request timeout in seconds")] = 30,
    cookie: Annotated[Optional[str], Query(description="BGG auth cookie")] = None,
    force_update: Annotated[bool, Query(description="Re-fetch credits for all games")] = False,
):
    job_id = create_job(
        "credits",
        config={
            "batch_size": batch_size,
            "delay_between_requests": delay_between_requests,
            "timeout": timeout,
            "force_update": force_update,
        },
    )
    thread = threading.Thread(
        target=run_credits_job,
        kwargs={
            "job_id": job_id,
            "batch_size": batch_size,
            "delay_between_requests": delay_between_requests,
            "timeout": timeout,
            "cookie": cookie,
            "force_update": force_update,
        },
    )
    thread.daemon = True
    thread.start()
    return {"job_id": job_id, "status": "pending", "type": "credits"}


@router.post(
    "/ratings",
    summary="Start ratings extraction",
    description="Start a background job that fetches BGG ratings for games in MongoDB "
    "that have no ratings yet (or all games if force_update=true), creates shadow users, and inserts ratings.",
)
async def start_ratings_extraction(
    batch_size: Annotated[int, Query(ge=1, le=100)] = 10,
    delay_between_requests: Annotated[float, Query(ge=0, le=60)] = 5.0,
    max_pages: Annotated[int, Query(ge=1, le=100, description="Max BGG pages per game")] = 30,
    timeout: Annotated[int, Query(ge=5, le=120)] = 30,
    cookie: Annotated[Optional[str], Query()] = None,
    force_update: Annotated[bool, Query(description="Re-fetch ratings (deletes existing for processed games)")] = False,
):
    job_id = create_job(
        "ratings",
        config={
            "batch_size": batch_size,
            "delay_between_requests": delay_between_requests,
            "max_pages": max_pages,
            "timeout": timeout,
            "force_update": force_update,
        },
    )
    thread = threading.Thread(
        target=run_ratings_job,
        kwargs={
            "job_id": job_id,
            "batch_size": batch_size,
            "delay_between_requests": delay_between_requests,
            "max_pages": max_pages,
            "timeout": timeout,
            "cookie": cookie,
            "force_update": force_update,
        },
    )
    thread.daemon = True
    thread.start()
    return {"job_id": job_id, "status": "pending", "type": "ratings"}
