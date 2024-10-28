# services/document_formatter.py

import logging
from typing import List

from abstract.format_service_base import FormatServiceBase
from services.schema import Document, Payload
import services.logger_base  # Ensure logging is configured

logger = logging.getLogger(__name__)


class DocumentFormatter(FormatServiceBase):
    """Service for formatting search results into documents."""

    def format_documents(self, search_results) -> List[Document]:
        """Formats search results into Document instances."""
        formatted_documents = []
        for hit in search_results:
            try:
                payload = Payload(
                    text=hit.payload.get("text", ""),
                    file_path=hit.payload.get("file_path")
                )
                document = Document(
                    payload=payload,
                    score=hit.score
                )
                formatted_documents.append(document)
            except Exception as e:
                logger.error(f"Error formatting document: {e}", exc_info=True)
                # Skip this document and continue with others
                continue
        logger.debug(f"Formatted {len(formatted_documents)} documents.")
        return formatted_documents