"""
Upload games CSV to MongoDB.
"""

import io
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from etl.load import DataLoader
from etl.logger import get_logger
from etl.transform import transform_game_from_csv

logger = get_logger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post(
    "/games",
    summary="Upload games CSV",
    description="Upload a CSV file of games (same format as test_bgg_games_*.csv). "
    "Games are upserted by bggId so existing games are updated.",
    response_description="Counts of inserted and updated documents",
)
async def upload_games(
    file: Annotated[UploadFile, File(description="CSV file with columns: bggId, name, detailUrl, rank, avgRating, numVoters, thumbnailUrl, yearPublished, description, etc.")],
    batch_size: Annotated[int, Query(description="Documents per batch for upsert", ge=1, le=5000)] = 1000,
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}") from e
    if "bggId" not in df.columns or "name" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain at least bggId and name columns",
        )
    if "bggId" in df.columns:
        df["bggId"] = df["bggId"].astype("Int64")

    games = []
    for _, row in df.iterrows():
        raw = row.to_dict()
        try:
            game = transform_game_from_csv(raw)
            if game.get("name") and game.get("bggId") is not None:
                games.append(game)
        except Exception as e:
            logger.warning("Skip row: %s", e)
            continue

    if not games:
        return {"uploaded": 0, "updated": 0, "message": "No valid games to upsert"}

    loader = DataLoader()
    try:
        loader.connect()
        inserted, modified = loader.upsert_games(games, batch_size=batch_size)
        return {"uploaded": inserted, "updated": modified}
    finally:
        loader.disconnect()
