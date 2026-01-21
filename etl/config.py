"""
ETL Configuration

Centralized configuration management using environment variables.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class MongoDBConfig:
    """MongoDB connection configuration."""

    uri: str
    database: str

    @classmethod
    def from_env(cls) -> "MongoDBConfig":
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI environment variable is required")

        return cls(
            uri=uri,
            database=os.getenv("MONGODB_DB", "board-game-recommender"),
        )


@dataclass
class CSVImportConfig:
    """CSV import configuration."""

    data_dir: Path
    file_pattern: str
    files_to_import: list[str]

    @classmethod
    def from_env(cls) -> "CSVImportConfig":
        # Default to etl/data relative to project root
        default_data_dir = Path(__file__).parent / "data"
        base_dir = Path(os.getenv("ETL_DATA_DIR", str(default_data_dir)))
        pattern = os.getenv("ETL_CSV_PATTERN", "_1_100")
        files_str = os.getenv("ETL_CSV_FILES", "games,ratings,credits")
        files = [f.strip() for f in files_str.split(",") if f.strip()]

        return cls(
            data_dir=base_dir,
            file_pattern=pattern,
            files_to_import=files,
        )


@dataclass
class PipelineConfig:
    """Pipeline execution configuration."""

    # Data directories
    data_dir: Path
    output_dir: Path

    # Pipeline stages to run
    run_bgg_extract: bool
    run_online_games_extract: bool
    run_transform: bool
    run_load: bool

    # Processing parameters
    min_reviews_per_game: int
    min_reviews_per_user: int
    batch_size: int

    # Retry configuration
    max_retries: int
    retry_delay: float

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        base_dir = Path(os.getenv("ETL_DATA_DIR", "./data"))

        return cls(
            data_dir=base_dir / "raw",
            output_dir=base_dir / "processed",
            run_bgg_extract=os.getenv("ETL_RUN_BGG", "false").lower() == "true",
            run_online_games_extract=os.getenv("ETL_RUN_ONLINE", "false").lower()
            == "true",
            run_transform=os.getenv("ETL_RUN_TRANSFORM", "true").lower() == "true",
            run_load=os.getenv("ETL_RUN_LOAD", "true").lower() == "true",
            min_reviews_per_game=int(os.getenv("ETL_MIN_REVIEWS_GAME", "500")),
            min_reviews_per_user=int(os.getenv("ETL_MIN_REVIEWS_USER", "5")),
            batch_size=int(os.getenv("ETL_BATCH_SIZE", "1000")),
            max_retries=int(os.getenv("ETL_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("ETL_RETRY_DELAY", "1.0")),
        )


@dataclass
class Config:
    """Main configuration container."""

    mongodb: MongoDBConfig
    pipeline: PipelineConfig
    csv_import: CSVImportConfig

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            mongodb=MongoDBConfig.from_env(),
            pipeline=PipelineConfig.from_env(),
            csv_import=CSVImportConfig.from_env(),
        )


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def ensure_directories(config: Config) -> None:
    """Ensure all required directories exist."""
    config.pipeline.data_dir.mkdir(parents=True, exist_ok=True)
    config.pipeline.output_dir.mkdir(parents=True, exist_ok=True)
