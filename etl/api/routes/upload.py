"""
Upload games CSV, credits CSV, and ratings CSV to MongoDB.
"""

import io
from datetime import datetime
from typing import Annotated, Any

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pymongo import UpdateOne

from etl.api.schemas import (
    UploadCreditsResponse,
    UploadGamesResponse,
    UploadRatingsResponse,
)
from etl.api.services.ratings_worker import _get_or_create_user_id
from etl.load import DataLoader
from etl.logger import get_logger
from etl.merge_csv_data import prepare_categories_mechanics
from etl.transform import transform_game_from_csv
from etl.lib.mongodb import COLLECTIONS
from etl.utils import clean_string, safe_float
from bson import ObjectId

logger = get_logger(__name__)

# CSV format documentation for upload endpoints
GAMES_CSV_FORMAT = (
    "Required columns: bggId (int), name (str). "
    "Optional: detailUrl, rank, avgRating, numVoters, geekRating, thumbnailUrl, "
    "yearPublished, description, page. Same format as test_bgg_games_*.csv."
)
CREDITS_CSV_FORMAT = (
    "Required column: bggId (int). "
    "Optional: mechanics (JSON array string), categories (JSON array string), "
    "designers (JSON array string), alternateNames, imageUrl, "
    "gameplay_numberofplayers, gameplay_playtime, gameplay_suggestedage. "
    "Same format as game_credits_*.csv. Mechanics/categories/designers are parsed as JSON arrays; "
    "gameplay_* are parsed into minPlayers, maxPlayers, minPlaytime, maxPlaytime, minAge."
)
RATINGS_CSV_FORMAT = (
    "Required columns: bggId (int), rating (float), username (str). "
    "Optional: rating_tstamp, isocountry, rating_count. Same format as game_ratings_*.csv."
)

router = APIRouter(prefix="/upload", tags=["upload"])


def _credits_row_to_game_update(row: Any) -> dict[str, Any]:
    """Build a MongoDB game $set doc from a credits row (after prepare_categories_mechanics)."""
    now = datetime.utcnow()
    mechanics = row.get("mechanics")
    if not isinstance(mechanics, list):
        mechanics = []
    categories = row.get("categories")
    if not isinstance(categories, list):
        categories = []
    designers_raw = row.get("designers")
    if not isinstance(designers_raw, list):
        designers_raw = []
    designers = [
        {"id": clean_string(n) or "", "name": clean_string(n), "url": None, "imageUrl": None}
        for n in designers_raw
        if n
    ]
    return {
        "mechanics": mechanics,
        "categories": categories,
        "designers": designers,
        "imageUrl": clean_string(row.get("imageUrl")),
        "minPlayers": row.get("minPlayers"),
        "maxPlayers": row.get("maxPlayers"),
        "minPlaytime": row.get("minPlaytime"),
        "maxPlaytime": row.get("maxPlaytime"),
        "minAge": row.get("minAge"),
        "updatedAt": now,
    }


@router.post(
    "/games",
    summary="Upload games CSV",
    description=(
        "Upload a games CSV. Rows are upserted by bggId (new games inserted, existing updated). "
        "CSV format: " + GAMES_CSV_FORMAT
    ),
    response_model=UploadGamesResponse,
)
async def upload_games(
    file: Annotated[UploadFile, File(description="Games CSV. Required headers: bggId, name.")],
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

    logger.info("Import games: starting, csv_rows=%s", len(df))
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
        logger.info("Import games: no valid rows to upsert")
        return {"uploaded": 0, "updated": 0, "message": "No valid games to upsert"}

    loader = DataLoader()
    try:
        loader.connect()
        inserted, modified = loader.upsert_games(games, batch_size=batch_size)
        logger.info("Import games: done, inserted=%s, updated=%s", inserted, modified)
        return {"uploaded": inserted, "updated": modified}
    finally:
        loader.disconnect()


@router.post(
    "/credits",
    summary="Upload credits CSV and merge with existing games",
    description=(
        "Upload a credits CSV. Only games already in MongoDB with a matching bggId are updated; "
        "parsing matches merge_csv_data (prepare_categories_mechanics). "
        "CSV format: " + CREDITS_CSV_FORMAT
    ),
    response_model=UploadCreditsResponse,
)
async def upload_credits(
    file: Annotated[UploadFile, File(description="Credits CSV. Required header: bggId.")],
    batch_size: Annotated[int, Query(description="Updates per batch", ge=1, le=5000)] = 1000,
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}") from e
    if "bggId" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain a bggId column")
    if "bggId" in df.columns:
        df["bggId"] = df["bggId"].astype("Int64")

    logger.info("Import credits: starting, csv_rows=%s", len(df))
    # Same parsing as merge_csv_data: mechanics, categories, designers, gameplay -> minPlayers, etc.
    df = prepare_categories_mechanics(df)

    updates = []
    for _, row in df.iterrows():
        bgg_id = row.get("bggId")
        if pd.isna(bgg_id) or bgg_id is None:
            continue
        try:
            update_doc = _credits_row_to_game_update(row)
            updates.append((int(bgg_id), update_doc))
        except Exception as e:
            logger.warning("Skip credits row bggId=%s: %s", bgg_id, e)
            continue

    if not updates:
        logger.info("Import credits: no valid rows to merge")
        return {"credits_rows": 0, "games_updated": 0, "message": "No valid credits rows to merge"}

    loader = DataLoader()
    try:
        loader.connect()
        collection = loader.mongo.get_collection(COLLECTIONS["GAMES"])
        games_updated = 0
        for i in range(0, len(updates), batch_size):
            batch = updates[i : i + batch_size]
            for bgg_id, update_doc in batch:
                result = collection.update_many(
                    {"bggId": bgg_id},
                    {"$set": update_doc},
                )
                games_updated += result.modified_count
        logger.info("Import credits: done, credits_rows=%s, games_updated=%s", len(updates), games_updated)
        return {
            "credits_rows": len(updates),
            "games_updated": games_updated,
        }
    finally:
        loader.disconnect()


@router.post(
    "/ratings",
    summary="Upload ratings CSV and merge with existing games and users",
    description=(
        "Upload a ratings CSV. Only rows whose bggId exists in the games collection are merged. "
        "Shadow users (shadow_bgg_{username}) are created as needed. "
        "Ratings are upserted by (userId, gameId); re-uploading updates existing ratings. "
        "CSV format: " + RATINGS_CSV_FORMAT
    ),
    response_model=UploadRatingsResponse,
)
async def upload_ratings(
    file: Annotated[UploadFile, File(description="Ratings CSV. Required headers: bggId, rating, username.")],
    batch_size: Annotated[int, Query(description="Upserts per batch", ge=1, le=5000)] = 5000,
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}") from e
    for col in ("bggId", "rating", "username"):
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"CSV must contain column: {col}")
    if "bggId" in df.columns:
        df["bggId"] = df["bggId"].astype("Int64")
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    logger.info("Import ratings: starting, csv_rows=%s", len(df))
    loader = DataLoader()
    try:
        loader.connect()
        games_coll = loader.mongo.get_collection(COLLECTIONS["GAMES"])
        ratings_coll = loader.mongo.get_collection(COLLECTIONS["RATINGS"])

        bgg_ids = df["bggId"].dropna().astype(int).unique().tolist()
        if not bgg_ids:
            logger.info("Import ratings: no valid bggIds in CSV")
            return {"ratings_rows": 0, "ratings_upserted": 0, "users_matched": 0, "games_matched": 0, "skipped": 0, "message": "No valid bggIds in CSV"}
        bgg_to_game = {}
        for doc in games_coll.find({"bggId": {"$in": bgg_ids}}, {"_id": 1, "bggId": 1}):
            bgg_to_game[doc["bggId"]] = doc["_id"]

        username_to_user_id = {}
        usernames = df["username"].dropna().astype(str).str.strip()
        usernames = usernames[usernames != ""].unique().tolist()
        for username in usernames:
            uid = _get_or_create_user_id(loader, username)
            if uid is not None:
                username_to_user_id[username] = uid

        now = datetime.utcnow()
        ops = []
        skipped = 0
        for _, row in df.iterrows():
            bgg_id = row.get("bggId")
            username = clean_string(str(row.get("username", "")).strip()) if row.get("username") else ""
            rating_val = safe_float(row.get("rating"))
            if pd.isna(bgg_id) or not username or rating_val is None:
                skipped += 1
                continue
            bgg_id_int = int(bgg_id)
            game_id = bgg_to_game.get(bgg_id_int)
            user_id = username_to_user_id.get(username)
            if game_id is None or user_id is None:
                skipped += 1
                continue
            ops.append(
                UpdateOne(
                    {"userId": user_id, "gameId": game_id},
                    {
                        "$set": {"rating": rating_val, "origin": "bgg", "updatedAt": now},
                        "$setOnInsert": {"_id": ObjectId(), "createdAt": now},
                    },
                    upsert=True,
                )
            )

        if not ops:
            logger.info("Import ratings: no valid rows to merge, skipped=%s", skipped)
            return {
                "ratings_rows": 0,
                "ratings_upserted": 0,
                "users_matched": 0,
                "games_matched": 0,
                "skipped": skipped,
                "message": "No valid ratings to merge (missing game or user)",
            }

        ratings_upserted = 0
        for i in range(0, len(ops), batch_size):
            batch = ops[i : i + batch_size]
            result = ratings_coll.bulk_write(batch)
            ratings_upserted += result.upserted_count + result.modified_count

        logger.info(
            "Import ratings: done, ratings_upserted=%s, users_matched=%s, games_matched=%s, skipped=%s",
            ratings_upserted,
            len(username_to_user_id),
            len(bgg_to_game),
            skipped,
        )
        return {
            "ratings_rows": len(ops),
            "ratings_upserted": ratings_upserted,
            "users_matched": len(username_to_user_id),
            "games_matched": len(bgg_to_game),
            "skipped": skipped,
        }
    finally:
        loader.disconnect()
