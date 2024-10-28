# tests/unit/test_search_service_handler.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from services.search_service_handler import SearchServiceHandler
from services.schema import SearchRequest, Document, Payload

@pytest.mark.asyncio
async def test_search_service_handler_perform_search():
    # Mock dependencies
    mock_search_service = AsyncMock()
    mock_search_service.search.return_value = [
        {'payload': {'text': 'Doc 1'}, 'score': 0.9}
    ]

    mock_embedding_service = AsyncMock()
    mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]

    # Use MagicMock for synchronous methods
    mock_format_service = MagicMock()
    mock_format_service.format_documents.return_value = [
        Document(payload=Payload(text='Formatted Doc 1', file_path='/path/doc1'), score=0.9)
    ]

    mock_summarization_service = AsyncMock()
    mock_summarization_service.summarize.return_value = 'Summarized text'

    handler = SearchServiceHandler(
        search_service=mock_search_service,
        embedding_service=mock_embedding_service,
        format_service=mock_format_service,
        summarization_service=mock_summarization_service,
    )

    request = SearchRequest(query='Sample query', k=5, summarizer=True)
    response = await handler.perform_search(request)

    # Assertions
    mock_embedding_service.generate_embedding.assert_awaited_once_with('Sample query')
    mock_search_service.search.assert_awaited_once()
    mock_format_service.format_documents.assert_called_once()  # Use assert_called_once
    mock_summarization_service.summarize.assert_awaited_once()
    assert response.summary == 'Summarized text'
