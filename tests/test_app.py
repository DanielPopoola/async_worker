import pytest
import asyncio
import aiohttp

@pytest.mark.asyncio
async def test_job_flow():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:8000/jobs',
                                json={'payload': {'task': 'hello_world', 'data': 123}}) as resp:
            job_data = await resp.json()
            job_id = job_data['job_id']
            print(f"Created job: {job_id}")

        for i in range(10):
            async with session.get(f'http://localhost:8000/jobs/{job_id}') as resp:
                status_data = await resp.json()
                print(f"Job {job_id} status: {status_data['status']}")

                if status_data['status'] in ['completed', 'failed']:
                    break

            await asyncio.sleep(1)

asyncio.run(test_job_flow())