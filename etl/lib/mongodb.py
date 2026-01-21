"""
MongoDB Helper for ETL Pipeline

Provides utilities for connecting to MongoDB and loading data.
"""

import os
import logging
from typing import Any, Optional
from datetime import datetime

import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MongoDBHelper:
    """MongoDB connection and data loading helper."""

    def __init__(
        self,
        uri: Optional[str] = None,
        database: Optional[str] = None,
    ):
        """
        Initialize MongoDB helper.

        Args:
            uri: MongoDB connection URI. Defaults to MONGODB_URI env var.
            database: Database name. Defaults to MONGODB_DB env var.
        """
        self.uri = uri or os.getenv("MONGODB_URI")
        self.database_name = database or os.getenv("MONGODB_DB", "board-game-recommender")

        if not self.uri:
            raise ValueError("MONGODB_URI environment variable not set")

        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        if self._client is None:
            logger.info(f"Connecting to MongoDB database: {self.database_name}")
            self._client = MongoClient(self.uri)
            self._db = self._client[self.database_name]
            # Test connection
            self._client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Disconnected from MongoDB")

    @property
    def db(self) -> Database:
        """Get database instance."""
        if self._db is None:
            self.connect()
        return self._db  # type: ignore

    def get_collection(self, name: str) -> Collection:
        """Get a collection by name."""
        return self.db[name]

    def upload_dataframe(
        self,
        collection_name: str,
        df: pd.DataFrame,
        batch_size: int = 1000,
        drop_existing: bool = False,
        upsert_key: Optional[str] = None,
    ) -> int:
        """
        Upload a pandas DataFrame to a MongoDB collection.

        Args:
            collection_name: Name of the collection.
            df: DataFrame to upload.
            batch_size: Number of documents per batch.
            drop_existing: If True, drop the collection before inserting.
            upsert_key: If provided, upsert documents by this key field.

        Returns:
            Number of documents inserted/updated.
        """
        collection = self.get_collection(collection_name)

        if drop_existing:
            collection.drop()
            logger.info(f"Dropped collection: {collection_name}")

        # Convert DataFrame to list of dicts
        records = df.to_dict(orient="records")
        total = len(records)

        if total == 0:
            logger.warning(f"No records to upload to {collection_name}")
            return 0

        # Add timestamps
        now = datetime.utcnow()
        for record in records:
            record["createdAt"] = now
            record["updatedAt"] = now

        # Upload in batches
        uploaded = 0
        for i in range(0, total, batch_size):
            batch = records[i : i + batch_size]

            if upsert_key:
                # Upsert mode
                operations = [
                    UpdateOne(
                        {upsert_key: doc[upsert_key]},
                        {"$set": doc},
                        upsert=True,
                    )
                    for doc in batch
                ]
                result = collection.bulk_write(operations)
                uploaded += result.upserted_count + result.modified_count
            else:
                # Insert mode
                result = collection.insert_many(batch)
                uploaded += len(result.inserted_ids)

            logger.info(
                f"Uploaded batch {i // batch_size + 1} "
                f"({min(i + batch_size, total)}/{total}) to {collection_name}"
            )

        logger.info(f"Completed upload to {collection_name}: {uploaded} documents")
        return uploaded

    def create_indexes(self, collection_name: str, indexes: list[dict]) -> None:
        """
        Create indexes on a collection.

        Args:
            collection_name: Name of the collection.
            indexes: List of index definitions with 'key' and optional options.
        """
        collection = self.get_collection(collection_name)

        for index_def in indexes:
            key = index_def["key"]
            options = {k: v for k, v in index_def.items() if k != "key"}
            try:
                index_name = collection.create_index(list(key.items()), **options)
                logger.info(f"Created index on {collection_name}: {index_name}")
            except Exception as e:
                logger.warning(f"Index creation failed on {collection_name}: {e}")


# Collection names (must match TypeScript schema)
COLLECTIONS = {
    "GAMES": "games",
    "USERS": "users",
    "RATINGS": "ratings",
    "RECOMMENDATIONS": "recommendations",
    "GAME_SIMILARITIES": "gameSimilarities",
    "ONLINE_GAMES": "onlineGames",
}

# Index definitions (must match TypeScript schema)
INDEXES = {
    "games": [
        {"key": {"bggId": 1}, "unique": True, "sparse": True},
        {"key": {"categories": 1}},
        {"key": {"mechanics": 1}},
        {"key": {"bggRating.average": -1}},
        {"key": {"bggRank": 1}},
        {"key": {"minPlayers": 1, "maxPlayers": 1}},
    ],
    "users": [
        {"key": {"clerkId": 1}, "unique": True},
    ],
    "ratings": [
        {"key": {"userId": 1, "gameId": 1}, "unique": True},
        {"key": {"userId": 1}},
        {"key": {"gameId": 1}},
    ],
    "recommendations": [
        {"key": {"userId": 1, "algorithm": 1}, "unique": True},
    ],
    "gameSimilarities": [
        {"key": {"gameId": 1}, "unique": True},
    ],
    "onlineGames": [
        {"key": {"gameId": 1}},
        {"key": {"bggId": 1}},
    ],
}


def initialize_database(helper: MongoDBHelper) -> None:
    """Initialize all collections with their indexes."""
    logger.info("Initializing database indexes...")

    for collection_name, indexes in INDEXES.items():
        helper.create_indexes(collection_name, indexes)

    logger.info("Database initialization complete")
