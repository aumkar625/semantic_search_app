# tests/integration/test_api.py

import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

# Add the root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, root_dir)  # Use insert(0, ...) to prioritize the root directory

import my_app  # Import the renamed module
fastapi_app = my_app.app

# Debug statements
print(f"Imported my_app module: {my_app}")
print(f"my_app.__file__: {getattr(my_app, '__file__', 'No __file__ attribute')}")
print(f"fastapi_app: {fastapi_app}")
print(f"type(fastapi_app): {type(fastapi_app)}")

@pytest.mark.asyncio
async def test_search_api():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/search", json={
            "query": "What is the capital of France?",
            "k": 2,
            "summarizer": True
        })
        assert response.status_code == 200
        data = response.json()
        assert 'documents' in data
        assert 'summary' in data
        assert len(data['documents']) <= 2
