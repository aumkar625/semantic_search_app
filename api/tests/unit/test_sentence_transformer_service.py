# tests/unit/test_sentence_transformer_service.py

import pytest
from unittest.mock import patch, MagicMock
from services.sentence_transformer_service import SentenceTransformerEmbeddingService

@pytest.mark.asyncio
@patch('services.sentence_transformer_service.SentenceTransformer')
async def test_sentence_transformer_generate_embedding(mock_sentence_transformer):
    # Mock the SentenceTransformer model
    mock_model_instance = MagicMock()
    mock_model_instance.encode.return_value = [0.1, 0.2, 0.3]
    mock_sentence_transformer.return_value = mock_model_instance

    # Set environment variables
    with patch.dict('os.environ', {'SENTENCE_TRANSFORMER': 'test_model'}):
        embedding_service = SentenceTransformerEmbeddingService()

    text = "Sample text"
    embedding = await embedding_service.generate_embedding(text)

    # Assertions
    mock_model_instance.encode.assert_called_once_with(text)
    assert embedding == [0.1, 0.2, 0.3]