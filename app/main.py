import os
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from .database import DatabaseManager
from .worker import SimpleWorker
from .models import JobCreateRequest, JobCreateResponse, JobStatusResponse
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "password")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME", "testdb")


db_manager: DatabaseManager | None = None
worker = None
worker_task = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_manager, worker, worker_task

    # Initialize db
    db_manager = DatabaseManager(f"postgresql://{user}:{password}@{host}/{dbname}")
    await db_manager.initialize()

    # Start worker
    worker = SimpleWorker(db_manager)
    worker_task = asyncio.create_task(worker.start())
    
    print("FastAPI app and worker started.")
    yield

    # Shutdown
    worker.stop()
    await worker_task
    await db_manager.close()
    print("FastAPI app and worker stopped")


app = FastAPI(lifespan=lifespan)

async def get_database() -> DatabaseManager:
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return db_manager


@app.post("/jobs", response_model=JobCreateResponse)
async def create_job(
    request: JobCreateRequest,
    db: DatabaseManager = Depends(get_database)
):
    try:
        existing_job_id = await db.find_duplicate_job(request.payload)
        if existing_job_id:
            job_id = await db.replace_duplicate_job(existing_job_id, request.payload)
        else:
            job_id = await db.create_job(request.payload)

        return JobCreateResponse(job_id=job_id, status="queued")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}" )
    
@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: DatabaseManager = Depends(get_database)
):
    try:
        job = await db.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobStatusResponse(
            job_id=job_id,
            status=job.status,
            attempt_count=job.attempt_count,
            payload=job.payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.get("/health")
async def health_check():
    try:
        if db_manager is not None:
            async with await db_manager._acquire_conn():
                return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")