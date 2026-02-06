"""
ETL Logging Configuration

Provides structured logging with file and console output.
Configure via ETL_LOG_LEVEL and ETL_LOG_DIR environment variables.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log dir: project root / logs (parent of etl package)
_DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging(
    level: Optional[str] = None,
    log_dir: Optional[Path] = None,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Defaults to env ETL_LOG_LEVEL or INFO.
        log_dir: Directory for log files. Defaults to env ETL_LOG_DIR or project root / logs.
        log_to_file: Whether to write logs to a file.

    Returns:
        Root logger instance
    """
    if level is None:
        level = os.getenv("ETL_LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    if log_dir is None:
        env_log_dir = os.getenv("ETL_LOG_DIR")
        log_dir = Path(env_log_dir) if env_log_dir else _DEFAULT_LOG_DIR

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(console_handler)

    # File handler: one file per day (etl_YYYY-MM-DD.log)
    if log_to_file:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"etl_{date_str}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        root_logger.addHandler(file_handler)

        root_logger.info("Logging to file: %s (level=%s)", log_file, level)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class PipelineProgress:
    """Helper for logging pipeline progress."""

    def __init__(self, name: str, total: int):
        self.name = name
        self.total = total
        self.current = 0
        self.logger = get_logger(name)
        self.start_time = datetime.now()

    def update(self, count: int = 1, message: str = "") -> None:
        """Update progress."""
        self.current += count
        pct = (self.current / self.total * 100) if self.total > 0 else 0

        elapsed = datetime.now() - self.start_time
        rate = self.current / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0

        msg = f"[{self.current}/{self.total}] ({pct:.1f}%) - {rate:.1f}/s"
        if message:
            msg += f" - {message}"

        self.logger.info(msg)

    def complete(self) -> None:
        """Mark progress as complete."""
        elapsed = datetime.now() - self.start_time
        self.logger.info(
            f"Completed {self.name}: {self.current} items in {elapsed.total_seconds():.1f}s"
        )
