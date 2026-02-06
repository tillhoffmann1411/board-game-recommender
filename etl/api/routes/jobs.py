"""
Get job status and stop a running job.
"""

from fastapi import APIRouter, HTTPException

from etl.api.job_store import get_job, request_cancel
from etl.api.schemas import JobResponse, StopJobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "/{job_id}",
    summary="Get job status",
    description=(
        "Return the job record: job_id, type (credits|ratings), status (pending|running|completed|failed|cancelled), "
        "progress (processed, total, errors; ratings_inserted for ratings jobs), "
        "started_at, finished_at, error (if failed), config."
    ),
    response_model=JobResponse,
)
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post(
    "/{job_id}/stop",
    summary="Stop a job",
    description=(
        "Request that a running or pending job stop. The job will finish its current item "
        "then exit with status 'cancelled'. Returns status 'cancelling' if stop was requested, "
        "or the current status and a message if the job was not running."
    ),
    response_model=StopJobResponse,
)
async def stop_job(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") not in ("pending", "running"):
        return {
            "job_id": job_id,
            "status": job.get("status"),
            "message": f"Job is not running (current status: {job.get('status')}).",
        }
    request_cancel(job_id)
    return {
        "job_id": job_id,
        "status": "cancelling",
        "message": "Stop requested. The job will exit after the current item.",
    }
