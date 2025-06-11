from unittest.mock import AsyncMock, patch
import pytest
from app.database import DatabaseManager, Job

@pytest.mark.asyncio
async def test_db_operation_mocked():
    db = DatabaseManager("fake-url")
    db.initialize = AsyncMock()
    db.create_job = AsyncMock(return_value="fake-id")
    db.get_next_job = AsyncMock(return_value=Job(id="fake-id", payload={"task": "test"}, status="claimed"))
    db.complete_job = AsyncMock()
    db.close = AsyncMock()

    await db.initialize()
    job_id = await db.create_job({"task": "test"})
    assert job_id == "fake-id"

    job = await db.get_next_job("worker-1")
    assert job.id == "fake-id"

    await db.complete_job(job.id)
    await db.close()

    db.initialize.assert_awaited_once()
    db.create_job.assert_called_once()
    db.get_next_job.assert_called_once()
    db.complete_job.assert_called_once_with("fake-id")
    db.close.assert_awaited_once()
