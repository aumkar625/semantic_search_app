# services/search_service_handler.py

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator

from fastapi import APIRouter, Depends
from services.schema import SearchRequest, SearchResponse
from services.service_factory import (
    get_search_service,
    get_format_service,
    get_embedding_service,
    get_summarization_service,
)
from services.search_service import SearchService
import services.logger_base  # Ensure logging is configured

logger = logging.getLogger(__name__)

# Define the APIRouter to handle search endpoints
search_router = APIRouter()


@contextmanager
def timeit(name: str) -> Generator[None, None, None]:
    start_time = time.perf_counter()
    yield
    elapsed_time = time.perf_counter() - start_time
    logger.debug(f"{name} completed in {elapsed_time:.4f} seconds.")


class SearchServiceHandler:
    """Service handler class to perform search and summarization logic."""

    def __init__(
        self,
        search_service: SearchService,
        embedding_service: Any,
        format_service: Any,
        summarization_service: Any,
    ):
        self.search_service = search_service
        self.embedding_service = embedding_service
        self.format_service = format_service
        self.summarization_service = summarization_service

    async def perform_search(self, request: SearchRequest) -> SearchResponse:
        logger.info("Received search request")

        try:
            # Generate embedding for the query
            with timeit("Embedding generation"):
                query_embedding = await self.embedding_service.generate_embedding(request.query)
                logger.debug(f"Query Embedding: {query_embedding}")

            # Search documents
            with timeit("Document search"):
                search_results = await self.search_service.search(query_embedding, request.k)
                logger.debug(f"Search Results: {search_results}")

            # Format documents
            with timeit("Document formatting"):
                formatted_documents = self.format_service.format_documents(search_results)
                logger.debug(f"Formatted Documents: {formatted_documents}")

            # Summarize if requested
            summary = ""
            if request.summarizer:
                with timeit("Summarization"):
                    # Pass request.query as the question to the summarization service
                    summary = await self.summarization_service.summarize(
                        [doc.payload.text for doc in formatted_documents[:5]], request.query
                    )
                    logger.debug(f"Summary: {summary}")

            logger.info("Processed search request")

            return SearchResponse(documents=formatted_documents, summary=summary)

        except Exception as e:
            logger.error(f"Error in perform_search: {e}", exc_info=True)
            raise


# Define a function to instantiate SearchServiceHandler with injected dependencies
def get_search_service_handler(
    search_service: SearchService = Depends(get_search_service),
    embedding_service=Depends(get_embedding_service),
    format_service=Depends(get_format_service),
    summarization_service=Depends(get_summarization_service),
):
    return SearchServiceHandler(
        search_service=search_service,
        embedding_service=embedding_service,
        format_service=format_service,
        summarization_service=summarization_service,
    )


@search_router.post("/api/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    search_service_handler: SearchServiceHandler = Depends(get_search_service_handler),
):
    return await search_service_handler.perform_search(request)
