"""
Pydantic schemas for ETL API request/response models.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Upload responses
# ---------------------------------------------------------------------------


class UploadGamesResponse(BaseModel):
    """Response from POST /upload/games."""

    uploaded: int = Field(..., description="Number of game documents inserted (new bggId).")
    updated: int = Field(..., description="Number of game documents updated (existing bggId).")
    message: Optional[str] = Field(None, description="Optional message, e.g. when no valid rows.")


class UploadCreditsResponse(BaseModel):
    """Response from POST /upload/credits."""

    credits_rows: int = Field(..., description="Number of credits rows processed from the CSV.")
    games_updated: int = Field(..., description="Number of game documents updated in MongoDB.")
    message: Optional[str] = Field(None, description="Optional message, e.g. when no valid rows.")


class UploadRatingsResponse(BaseModel):
    """Response from POST /upload/ratings."""

    ratings_rows: int = Field(..., description="Number of rating rows that were valid and merged.")
    ratings_upserted: int = Field(..., description="Number of rating documents inserted or updated.")
    users_matched: int = Field(..., description="Number of distinct usernames resolved (shadow users).")
    games_matched: int = Field(..., description="Number of distinct games (bggId) that had at least one rating.")
    skipped: int = Field(..., description="Number of CSV rows skipped (invalid or no matching game/user).")
    message: Optional[str] = Field(None, description="Optional message, e.g. when no valid rows.")


# ---------------------------------------------------------------------------
# Extract (job start) responses
# ---------------------------------------------------------------------------


class JobStartedResponse(BaseModel):
    """Response from POST /extract/credits and POST /extract/ratings."""

    job_id: str = Field(..., description="Unique job identifier (UUID).")
    status: str = Field(..., description="Initial status, e.g. 'pending'.")
    type: str = Field(..., description="Job type: 'credits' or 'ratings'.")


# ---------------------------------------------------------------------------
# Stats response
# ---------------------------------------------------------------------------


class JobProgress(BaseModel):
    """Progress info for a job."""

    processed: int = 0
    total: int = 0
    errors: int = 0
    ratings_inserted: Optional[int] = Field(None, description="Present for ratings jobs.")


class JobInList(BaseModel):
    """Job record as returned in list/stats."""

    job_id: str
    type: str = Field(..., description="'credits' or 'ratings'.")
    status: str = Field(..., description="pending, running, completed, failed, cancelled.")
    progress: dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)
    cancel_requested: Optional[bool] = None


class StatsResponse(BaseModel):
    """Response from GET /stats."""

    total_games: int = Field(..., description="Total number of games in the database.")
    games_with_credits: int = Field(
        ...,
        description="Games that have at least one of mechanics, categories, or designers set.",
    )
    games_with_ratings: int = Field(
        ...,
        description="Number of distinct games that have at least one rating.",
    )
    games_with_all_data: int = Field(
        ...,
        description="Games that have both credits and at least one rating.",
    )
    jobs: list[JobInList] = Field(..., description="List of jobs (running and/or recent).")


# ---------------------------------------------------------------------------
# Job detail and stop
# ---------------------------------------------------------------------------


class JobResponse(BaseModel):
    """Response from GET /jobs/{job_id}. Full job record."""

    job_id: str
    type: str
    status: str
    progress: dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)
    cancel_requested: Optional[bool] = None


class StopJobResponse(BaseModel):
    """Response from POST /jobs/{job_id}/stop."""

    job_id: str = Field(..., description="The job identifier.")
    status: str = Field(
        ...,
        description="'cancelling' if stop was requested, or current status if job was not running.",
    )
    message: str = Field(..., description="Human-readable message.")


# ---------------------------------------------------------------------------
# Root / health
# ---------------------------------------------------------------------------


class RootResponse(BaseModel):
    """Response from GET /."""

    service: str = Field(..., description="API name.")
    docs: str = Field(..., description="Path to Swagger UI.")
    redoc: str = Field(..., description="Path to ReDoc.")
    endpoints: dict[str, str] = Field(..., description="Map of endpoint name to method and path.")
