# tests/unit/test_summarization_service.py

import pytest
from unittest.mock import patch, AsyncMock, MagicMock  # Add MagicMock
from services.summarization_service import SummarizationService

@pytest.mark.asyncio
@patch('services.summarization_service.genai')
async def test_summarization_service_summarize(mock_genai):
    # Mock the generative AI model
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = MagicMock(text='Summarized text')
    mock_genai.configure.return_value = None
    mock_genai.GenerativeModel.return_value = mock_model_instance

    # Set environment variables
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key', 'GEMINI_MODEL_SUMMARY': 'test_model'}):
        summarization_service = SummarizationService()

    texts = ["Text 1", "Text 2"]
    question = "What is the summary?"
    summary = await summarization_service.summarize(texts, question)

    # Assertions
    mock_model_instance.generate_content.assert_called_once()
    assert summary == 'Summarized text'