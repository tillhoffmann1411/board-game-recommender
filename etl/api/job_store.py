"""
In-memory job store for ETL extraction jobs (credits, ratings).
Thread-safe; workers update status and progress.
"""

import threading
import uuid
from datetime import datetime
from typing import Any, Optional

# In-memory store: job_id -> job record
_jobs: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


def create_job(
    job_type: str,
    config: Optional[dict[str, Any]] = None,
) -> str:
    """Create a new job record and return its id."""
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "status": "pending",
            "progress": {"processed": 0, "total": 0, "errors": 0},
            "started_at": None,
            "finished_at": None,
            "error": None,
            "config": config or {},
            "cancel_requested": False,
        }
    return job_id


def get_job(job_id: str) -> Optional[dict[str, Any]]:
    """Return the job record if it exists."""
    with _lock:
        return _jobs.get(job_id)


def update_job(
    job_id: str,
    *,
    status: Optional[str] = None,
    progress: Optional[dict[str, Any]] = None,
    started_at: Optional[datetime] = None,
    finished_at: Optional[datetime] = None,
    error: Optional[str] = None,
) -> None:
    """Update a job's fields."""
    with _lock:
        if job_id not in _jobs:
            return
        rec = _jobs[job_id]
        if status is not None:
            rec["status"] = status
        if progress is not None:
            rec["progress"] = progress
        if started_at is not None:
            rec["started_at"] = started_at.isoformat()
        if finished_at is not None:
            rec["finished_at"] = finished_at.isoformat()
        if error is not None:
            rec["error"] = error


def request_cancel(job_id: str) -> bool:
    """Request that a running job stop. Returns True if the job exists and cancel was set."""
    with _lock:
        if job_id not in _jobs:
            return False
        _jobs[job_id]["cancel_requested"] = True
        return True


def is_cancel_requested(job_id: str) -> bool:
    """Return whether cancel has been requested for this job."""
    with _lock:
        rec = _jobs.get(job_id)
        return bool(rec and rec.get("cancel_requested"))


def list_jobs(
    status_filter: Optional[str] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List jobs, optionally filtered by status, most recent first."""
    with _lock:
        jobs = list(_jobs.values())
    if status_filter:
        jobs = [j for j in jobs if j.get("status") == status_filter]
    # Sort by started_at desc (None last)
    jobs.sort(
        key=lambda j: j.get("started_at") or "",
        reverse=True,
    )
    return jobs[:limit]
