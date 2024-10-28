# tests/unit/test_qdrant_service.py

import pytest
from unittest.mock import patch, AsyncMock
from services.qdrant_service import QdrantService


@pytest.mark.asyncio
@patch('services.qdrant_service.QdrantClient')
async def test_qdrant_service_search(mock_qdrant_client):
    # Mock the Qdrant client
    mock_client_instance = mock_qdrant_client.return_value
    mock_client_instance.search.return_value = [{'id': 1, 'score': 0.9}]

    # Set environment variables for testing
    with patch.dict('os.environ', {'QDRANT_URL': 'http://localhost:6333', 'TABLE': 'test_collection'}):
        qdrant_service = QdrantService()

    query_embedding = [0.1, 0.2, 0.3]
    k = 5
    results = await qdrant_service.search(query_embedding, k)

    # Assertions
    mock_client_instance.search.assert_called_once()
    assert results == [{'id': 1, 'score': 0.9}]