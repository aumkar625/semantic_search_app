# tests/unit/test_search_service.py

import pytest
from unittest.mock import AsyncMock
from services.search_service import SearchService

@pytest.mark.asyncio
async def test_search_service_search():
    # Create a mock vector_db_service
    mock_vector_db_service = AsyncMock()
    mock_vector_db_service.search = AsyncMock(return_value=[{'id': 1, 'score': 0.9}])

    # Instantiate SearchService with the mock
    search_service = SearchService(vector_db_service=mock_vector_db_service)

    # Call the search method
    query_embedding = [0.1, 0.2, 0.3]
    k = 5
    results = await search_service.search(query_embedding, k)

    # Assertions
    mock_vector_db_service.search.assert_awaited_once_with(query_embedding, k)
    assert results == [{'id': 1, 'score': 0.9}]

