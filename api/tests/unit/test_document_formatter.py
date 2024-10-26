# tests/unit/test_document_formatter.py

from services.document_formatter import DocumentFormatter
from services.schema import Document, Payload
from unittest.mock import MagicMock  # Add this import

def test_document_formatter():
    formatter = DocumentFormatter()

    # Sample search results
    search_results = [
        MagicMock(payload={'text': 'Doc 1', 'file_path': '/path/doc1'}, score=0.9),
        MagicMock(payload={'text': 'Doc 2', 'file_path': '/path/doc2'}, score=0.8),
    ]

    formatted_documents = formatter.format_documents(search_results)

    # Assertions
    assert len(formatted_documents) == 2
    assert isinstance(formatted_documents[0], Document)
    assert formatted_documents[0].payload.text == 'Doc 1'
    assert formatted_documents[0].score == 0.9
