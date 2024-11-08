# services/qdrant_service.py

import os
import logging
import asyncio

from abstract.vector_db_base import VectorDBBase
from qdrant_client import QdrantClient
import services.logger_base  # Ensure logging is configured

logger = logging.getLogger(__name__)


class QdrantService(VectorDBBase):
    """Service for interacting with Qdrant vector database."""

    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.collection_name = os.getenv('TABLE')
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        logger.info(f"Qdrant client initialized with URL: {self.qdrant_url}")

    async def search(self, query_embedding, k: int):
        """Performs a search in the Qdrant database."""
        try:
            results = await asyncio.to_thread(
                self.client.search,
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k
            )
            logger.debug(f"Qdrant search results: {results}")
            return results
        except Exception as e:
            logger.error(f"Error during Qdrant search: {e}", exc_info=True)
            raise