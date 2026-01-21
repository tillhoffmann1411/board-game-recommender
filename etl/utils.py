"""
ETL Utilities

Common utilities for the ETL pipeline including retry handling and data transformations.
"""

import functools
import time
from typing import Any, Callable, TypeVar, Optional
import requests

from etl.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception: Optional[Exception] = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )

            raise last_exception  # type: ignore

        return wrapper

    return decorator


@retry(max_attempts=3, delay=1.0, exceptions=(requests.RequestException,))
def fetch_json(url: str, params: Optional[dict] = None, timeout: int = 30) -> dict:
    """
    Fetch JSON from a URL with retry handling.

    Args:
        url: URL to fetch
        params: Query parameters
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON response
    """
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


@retry(max_attempts=3, delay=1.0, exceptions=(requests.RequestException,))
def fetch_paginated(
    url: str,
    params: Optional[dict] = None,
    page_key: str = "page",
    results_key: str = "results",
    max_pages: Optional[int] = None,
) -> list:
    """
    Fetch all pages from a paginated API.

    Args:
        url: Base URL
        params: Query parameters
        page_key: Parameter name for page number
        results_key: Key in response containing results
        max_pages: Maximum pages to fetch (None for all)

    Returns:
        List of all results across pages
    """
    all_results = []
    page = 1
    params = params or {}

    while True:
        params[page_key] = page
        response = fetch_json(url, params)

        results = response.get(results_key, [])
        if not results:
            break

        all_results.extend(results)
        logger.debug(f"Fetched page {page}: {len(results)} results")

        if max_pages and page >= max_pages:
            break

        page += 1

    return all_results


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.

    Args:
        data: Dictionary to extract from
        *keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Value at the nested key path or default
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result


def clean_string(value: Any) -> Optional[str]:
    """Clean and normalize a string value."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def safe_int(value: Any) -> Optional[int]:
    """Safely convert to int."""
    if value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_float(value: Any) -> Optional[float]:
    """Safely convert to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of specified size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
