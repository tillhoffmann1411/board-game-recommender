"""
ETL Data Loader

Loads transformed data into MongoDB.
"""

from datetime import datetime
from typing import Optional

from pymongo import UpdateOne

from etl.lib.mongodb import MongoDBHelper, COLLECTIONS, initialize_database
from etl.logger import get_logger, PipelineProgress
from etl.config import get_config

logger = get_logger(__name__)


class DataLoader:
    """Loads ETL data into MongoDB."""

    def __init__(self, mongo: Optional[MongoDBHelper] = None):
        """
        Initialize the data loader.

        Args:
            mongo: MongoDB helper instance. If None, creates from config.
        """
        if mongo is None:
            config = get_config()
            self.mongo = MongoDBHelper(
                uri=config.mongodb.uri,
                database=config.mongodb.database,
            )
        else:
            self.mongo = mongo

        self._connected = False

    def connect(self) -> None:
        """Connect to MongoDB."""
        if not self._connected:
            self.mongo.connect()
            self._connected = True

    def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self._connected:
            self.mongo.disconnect()
            self._connected = False

    def initialize(self) -> None:
        """Initialize database with indexes."""
        self.connect()
        initialize_database(self.mongo)
        logger.info("Database initialized")

    def load_games(
        self,
        games: list[dict],
        batch_size: int = 1000,
        drop_existing: bool = False,
    ) -> int:
        """
        Load games into MongoDB.

        Args:
            games: List of game documents
            batch_size: Documents per batch
            drop_existing: Drop collection before loading

        Returns:
            Number of documents loaded
        """
        self.connect()
        collection = self.mongo.get_collection(COLLECTIONS["GAMES"])

        if drop_existing:
            collection.drop()
            logger.info("Dropped games collection")

        progress = PipelineProgress("games", len(games))
        loaded = 0

        for i in range(0, len(games), batch_size):
            batch = games[i : i + batch_size]
            result = collection.insert_many(batch)
            loaded += len(result.inserted_ids)
            progress.update(len(batch))

        progress.complete()
        return loaded

    def upsert_games(
        self,
        games: list[dict],
        batch_size: int = 1000,
    ) -> tuple[int, int]:
        """
        Upsert games into MongoDB by bggId. New games are inserted; existing are updated.

        Args:
            games: List of game documents (each must have bggId)
            batch_size: Documents per batch for bulk_write

        Returns:
            Tuple of (inserted_count, modified_count)
        """
        self.connect()
        collection = self.mongo.get_collection(COLLECTIONS["GAMES"])
        now = datetime.utcnow()
        inserted = 0
        modified = 0

        for i in range(0, len(games), batch_size):
            batch = games[i : i + batch_size]
            operations = []
            for doc in batch:
                bgg_id = doc.get("bggId")
                if bgg_id is None:
                    continue
                # Fields to set on every write (update or insert); exclude _id and createdAt
                set_doc = {
                    k: v
                    for k, v in doc.items()
                    if k not in ("_id", "createdAt")
                }
                set_doc["updatedAt"] = now
                # On insert only: _id and createdAt
                set_on_insert = {
                    "_id": doc["_id"],
                    "createdAt": doc.get("createdAt", now),
                }
                operations.append(
                    UpdateOne(
                        {"bggId": bgg_id},
                        {
                            "$set": set_doc,
                            "$setOnInsert": set_on_insert,
                        },
                        upsert=True,
                    )
                )
            if operations:
                result = collection.bulk_write(operations)
                inserted += result.upserted_count
                modified += result.modified_count

        logger.info(f"Upserted games: {inserted} inserted, {modified} updated")
        return inserted, modified

    def load_users(
        self,
        users: list[dict],
        batch_size: int = 5000,
        drop_existing: bool = False,
    ) -> int:
        """
        Load users into MongoDB.

        Args:
            users: List of user documents
            batch_size: Documents per batch
            drop_existing: Drop collection before loading

        Returns:
            Number of documents loaded
        """
        self.connect()
        collection = self.mongo.get_collection(COLLECTIONS["USERS"])

        if drop_existing:
            collection.drop()
            logger.info("Dropped users collection")

        progress = PipelineProgress("users", len(users))
        loaded = 0

        for i in range(0, len(users), batch_size):
            batch = users[i : i + batch_size]
            result = collection.insert_many(batch)
            loaded += len(result.inserted_ids)
            progress.update(len(batch))

        progress.complete()
        return loaded

    def load_ratings(
        self,
        ratings: list[dict],
        batch_size: int = 10000,
        drop_existing: bool = False,
    ) -> int:
        """
        Load ratings into MongoDB.

        Args:
            ratings: List of rating documents
            batch_size: Documents per batch
            drop_existing: Drop collection before loading

        Returns:
            Number of documents loaded
        """
        self.connect()
        collection = self.mongo.get_collection(COLLECTIONS["RATINGS"])

        if drop_existing:
            collection.drop()
            logger.info("Dropped ratings collection")

        progress = PipelineProgress("ratings", len(ratings))
        loaded = 0

        for i in range(0, len(ratings), batch_size):
            batch = ratings[i : i + batch_size]
            result = collection.insert_many(batch)
            loaded += len(result.inserted_ids)
            progress.update(len(batch))

        progress.complete()
        return loaded

    def load_similarities(
        self,
        similarities: list[dict],
        batch_size: int = 1000,
        drop_existing: bool = False,
    ) -> int:
        """
        Load game similarities into MongoDB.

        Args:
            similarities: List of similarity documents
            batch_size: Documents per batch
            drop_existing: Drop collection before loading

        Returns:
            Number of documents loaded
        """
        self.connect()
        collection = self.mongo.get_collection(COLLECTIONS["GAME_SIMILARITIES"])

        if drop_existing:
            collection.drop()
            logger.info("Dropped similarities collection")

        progress = PipelineProgress("similarities", len(similarities))
        loaded = 0

        for i in range(0, len(similarities), batch_size):
            batch = similarities[i : i + batch_size]
            result = collection.insert_many(batch)
            loaded += len(result.inserted_ids)
            progress.update(len(batch))

        progress.complete()
        return loaded

    def load_online_games(
        self,
        online_games: list[dict],
        batch_size: int = 1000,
        drop_existing: bool = False,
    ) -> int:
        """
        Load online games into MongoDB.

        Args:
            online_games: List of online game documents
            batch_size: Documents per batch
            drop_existing: Drop collection before loading

        Returns:
            Number of documents loaded
        """
        self.connect()
        collection = self.mongo.get_collection(COLLECTIONS["ONLINE_GAMES"])

        if drop_existing:
            collection.drop()
            logger.info("Dropped online games collection")

        if not online_games:
            logger.warning("No online games to load")
            return 0

        progress = PipelineProgress("online_games", len(online_games))
        loaded = 0

        for i in range(0, len(online_games), batch_size):
            batch = online_games[i : i + batch_size]
            result = collection.insert_many(batch)
            loaded += len(result.inserted_ids)
            progress.update(len(batch))

        progress.complete()
        return loaded

    def get_stats(self) -> dict[str, int]:
        """Get document counts for all collections."""
        self.connect()
        stats = {}

        for name, collection_name in COLLECTIONS.items():
            count = self.mongo.get_collection(collection_name).count_documents({})
            stats[collection_name] = count

        return stats
