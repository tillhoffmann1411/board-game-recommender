"""
ETL Logging Configuration

Provides structured logging with file and console output.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_dir: Optional[Path] = None,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files. Defaults to ./logs
        log_to_file: Whether to write logs to a file

    Returns:
        Root logger instance
    """
    # Get numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

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

    # File handler
    if log_to_file:
        if log_dir is None:
            log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"etl_{timestamp}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        root_logger.addHandler(file_handler)

        root_logger.info(f"Logging to file: {log_file}")

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
