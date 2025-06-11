import asyncio
import uuid
from .database import DatabaseManager


class SimpleWorker:
    def __init__(self, database_manger: DatabaseManager):
        self.db = database_manger
        self.worker_id = str(uuid.uuid4())
        self.running = False

    async def start(self):
        """Start the worker loop"""
        self.running = True
        print(f"Worker {self.worker_id} starting...")

        while self.running:
            try:
                job = await self.db.get_next_job(self.worker_id)

                if job:
                    print(f"Processing job {job.id}")
                    await self.process_job(job)
                else:
                    # No jobs available
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(5)

    async def process_job(self, job):
        """Processes a single job"""
        try:
            await asyncio.sleep(2)

            print(f"Processed job {job.id}: {job.payload}")

            await self.db.complete_job(job.id)
        except Exception as e:
            await self.db.fail_job(job.id, str(e))

    def stop(self):
        """Stop the worker."""
        self.running = False
        print(f"Worker {self.worker_id} stopping...")