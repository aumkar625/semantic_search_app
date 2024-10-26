# services/search_service.py

import logging
from abstract.search_service_base import SearchServiceBase
from abstract.vector_db_base import VectorDBBase
import services.logger_base  # Ensure logging is configured

logger = logging.getLogger(__name__)


class SearchService(SearchServiceBase):
    """Service for performing vector-based searches."""

    def __init__(self, vector_db_service: VectorDBBase):
        self.vector_db_service = vector_db_service
        logger.info("SearchService initialized.")

    async def search(self, query_embedding, k: int):
        """Performs a search using the vector database service."""
        try:
            # Directly await the async method
            results = await self.vector_db_service.search(query_embedding, k)
            logger.debug("Search completed.")
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}", exc_info=True)
            raise