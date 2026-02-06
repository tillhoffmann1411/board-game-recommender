"""
ETL API server.

Run with: uvicorn etl.api.main:app --host 0.0.0.0 --port 8000
Swagger UI: /docs

Logging is configured from env on import: ETL_LOG_LEVEL, ETL_LOG_DIR.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from etl.api.routes import extract, jobs, stats, upload
from etl.api.schemas import RootResponse
from etl.logger import setup_logging

# Configure logging from env when API starts (level + log dir; one file per day)
setup_logging(log_to_file=True)

app = FastAPI(
    title="ETL API",
    description="Upload games CSV, run credits/ratings extraction jobs, and view statistics.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(stats.router)
app.include_router(jobs.router)


@app.get(
    "/",
    tags=["health"],
    summary="Health and API info",
    description="Returns service name, links to docs, and a map of available endpoints.",
    response_model=RootResponse,
)
async def root():
    """Health check and API info."""
    return {
        "service": "ETL API",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "upload_games": "POST /upload/games",
            "upload_credits": "POST /upload/credits",
            "upload_ratings": "POST /upload/ratings",
            "extract_credits": "POST /extract/credits",
            "extract_ratings": "POST /extract/ratings",
            "stats": "GET /stats",
            "job": "GET /jobs/{job_id}",
            "stop_job": "POST /jobs/{job_id}/stop",
        },
    }
