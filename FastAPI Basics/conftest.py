import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from main import app 

@pytest_asyncio.fixture
async def async_test_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test") as client:
        yield client
