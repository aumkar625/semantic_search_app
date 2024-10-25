from fastapi import APIRouter, Depends
from services.schema import SearchRequest, SearchResponse
from services.service_factory import (
    get_search_service, get_format_service, get_embedding_service, get_summarization_service
)
from services.search_service import SearchService

# Define the APIRouter to handle search endpoints
search_router = APIRouter()

class SearchServiceHandler:
    """Service handler class to perform search and summarization logic."""

    def __init__(self, search_service, embedding_service, format_service, summarization_service):
        self.search_service = search_service
        self.embedding_service = embedding_service
        self.format_service = format_service
        self.summarization_service = summarization_service

    async def perform_search(self, request: SearchRequest) -> SearchResponse:
        # Generate embedding for the query
        query_embedding = self.embedding_service.generate_embedding(request.query)

        # Search and format documents
        search_results = self.search_service.search(query_embedding, request.k)
        formatted_documents = self.format_service.format_documents(search_results)

        # Summarize if requested
        summary = ""
        if request.summarizer:
            summary = self.summarization_service.summarize(
                [doc.payload.text for doc in formatted_documents[:5]], request.summarizer
            )

        return SearchResponse(documents=formatted_documents, summary=summary)

# Define a function to instantiate SearchServiceHandler with injected dependencies
def get_search_service_handler(
    search_service: SearchService = Depends(get_search_service),
    embedding_service=Depends(get_embedding_service),
    format_service=Depends(get_format_service),
    summarization_service=Depends(get_summarization_service)
):
    return SearchServiceHandler(
        search_service=search_service,
        embedding_service=embedding_service,
        format_service=format_service,
        summarization_service=summarization_service
    )

@search_router.post("/api/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    search_service_handler: SearchServiceHandler = Depends(get_search_service_handler)
):
    return await search_service_handler.perform_search(request)
