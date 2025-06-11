import asyncpg
import asyncio
from typing import Optional
from dataclasses import dataclass
import json


@dataclass
class Job:
    id: str
    payload: dict
    status: str
    attempt_count: int = 0


class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def initialize(self):
        """Create a connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=5
            )

    async def close(self):
        """Clean shutdown."""
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def _acquire_conn(self):
        if self.pool is None:
            raise RuntimeError("Database connection pool not initialized. Call `await initialize()` first.")
        return self.pool.acquire()

    async def create_job(self, payload: dict) -> str:
        """Insert a new job, return job ID."""
        async with await self._acquire_conn() as conn:
            job_id = await conn.fetchval(
                "INSERT INTO jobs (payload) VALUES ($1) RETURNING id",
                json.dumps(payload)
            )
            return str(job_id)
        
    async def get_next_job(self, worker_id: str) -> Optional[Job]:
        """Claim next available job - the core method"""
        async with await self._acquire_conn() as conn:
            row = await conn.fetchrow("""
                UPDATE jobs
                SET status = 'processing',
                    worker_id = $1,
                    started_at = NOW()
                WHERE id = (
                    SELECT id FROM jobs
                    WHERE status = 'queued'
                    ORDER BY created_at
                    LIMIT 1 FOR UPDATE SKIP LOCKED
                )
                RETURNING id, payload, status, attempt_count
            """, worker_id)

            if row:
                return Job(
                    id=str(row['id']),
                    payload=json.loads(row['payload']),
                    status=row['status'],
                    attempt_count=row['attempt_count']
                )
            return None
        
    async def complete_job(self, job_id: str):
            """Mark job as completed."""
            async with await self._acquire_conn() as conn:
                await conn.execute(
                    "UPDATE jobs SET status = 'completed', completed_at = NOW() WHERE id = $1",
                    job_id
                )

    async def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed"""
        async with await self._acquire_conn() as conn:
            await conn.execute(
                "UPDATE jobs SET status = 'failed', last_error = $1 WHERE id = $2",
                error_message, job_id
            )

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Get job by ID for status checking."""
        async with await self._acquire_conn() as conn:
            row = await conn.fetchrow(
                "SELECT id, payload, status, attempt_count FROM jobs WHERE id = $1",
                job_id
            )

            if row:
                return Job(
                    id=str(row['id']),
                    payload=json.loads(row['payload']),
                    status=row['status'],
                    attempt_count=row['attempt_count']
                )
            return None
        
    async def find_duplicate_job(self, payload: dict) -> Optional[str]:
        """Checks if a job with identical payload exists."""
        async with await self._acquire_conn() as conn:
            job_id = await conn.fetchval(
                "SELECT id FROM jobs WHERE payload = $1 AND status IN ('queued', 'processing')",
                json.dumps(payload, sort_keys=True)
            )
            return str(job_id) if job_id else None
        
    async def replace_duplicate_job(self, old_job_id: str, new_payload: dict) -> str:
        """Replace an existing job with a new payload."""
        async with await self._acquire_conn() as conn:
            await conn.execute("""
                UPDATE jobs
                SET payload = $1,
                    status = 'queued',
                    attempt_count = 0,
                    created_at = NOW(),
                    worker_id = NULL,
                    started_at = NULL
                WHERE id = $2
            """, json.dumps(new_payload), old_job_id)
            return old_job_id