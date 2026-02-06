"""
Get job status and stop a running job.
"""

from fastapi import APIRouter, HTTPException

from etl.api.job_store import get_job, request_cancel

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "/{job_id}",
    summary="Get job status",
    description="Return status, progress, and error (if failed) for a job.",
)
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post(
    "/{job_id}/stop",
    summary="Stop a job",
    description="Request that a running job stop. The job will finish its current item "
    "and then exit with status 'cancelled'. Idempotent for unknown or already-finished jobs.",
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
