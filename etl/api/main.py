"""
ETL API server.

Run with: uvicorn etl.api.main:app --host 0.0.0.0 --port 8000
Swagger UI: /docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from etl.api.routes import extract, jobs, stats, upload

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


@app.get("/", tags=["health"])
async def root():
    """Health check and API info."""
    return {
        "service": "ETL API",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "upload": "POST /upload/games",
            "extract_credits": "POST /extract/credits",
            "extract_ratings": "POST /extract/ratings",
            "stats": "GET /stats",
            "job": "GET /jobs/{job_id}",
            "stop_job": "POST /jobs/{job_id}/stop",
        },
    }
