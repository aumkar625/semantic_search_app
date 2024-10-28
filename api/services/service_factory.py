# services/service_factory.py

import os
import logging
from functools import lru_cache

from services.qdrant_service import QdrantService
from services.sentence_transformer_service import SentenceTransformerEmbeddingService
from services.summarization_service import SummarizationService
from services.document_formatter import DocumentFormatter
from services.search_service import SearchService
from services.prompt_service import FilePromptService
from abstract.vector_db_base import VectorDBBase
from abstract.embedding_base import EmbeddingServiceBase
from abstract.summarization_base import SummarizationBase
from abstract.prompt_base import PromptBase
import services.logger_base

logger = logging.getLogger(__name__)


@lru_cache()
def get_vector_db_service() -> VectorDBBase:
    """Get the vector database service instance based on environment configuration."""
    db_type = os.getenv("VECTOR_DB_TYPE", "qdrant")
    if db_type == "qdrant":
        logger.info("Initializing QdrantService.")
        return QdrantService()
    else:
        raise ValueError(f"Unsupported VECTOR_DB_TYPE: {db_type}")


@lru_cache()
def get_embedding_service() -> EmbeddingServiceBase:
    """Get the embedding service instance."""
    embedding_type = os.getenv("EMBEDDING_SERVICE_TYPE", "sentence_transformer")
    if embedding_type == "sentence_transformer":
        logger.info("Initializing SentenceTransformerEmbeddingService.")
        return SentenceTransformerEmbeddingService()
    else:
        raise ValueError(f"Unsupported EMBEDDING_SERVICE_TYPE: {embedding_type}")


@lru_cache()
def get_summarization_service() -> SummarizationBase:
    """Get the summarization service instance."""
    summarizer_type = os.getenv("SUMMARIZATION_SERVICE_TYPE", "default")
    if summarizer_type == "default":
        logger.info("Initializing SummarizationService.")
        return SummarizationService()
    else:
        raise ValueError(f"Unsupported SUMMARIZATION_SERVICE_TYPE: {summarizer_type}")


@lru_cache()
def get_search_service() -> SearchService:
    """Provides the search service."""
    logger.info("Initializing SearchService.")
    vector_db_service = get_vector_db_service()
    return SearchService(vector_db_service=vector_db_service)


@lru_cache()
def get_format_service() -> DocumentFormatter:
    """Provides the document formatter service."""
    logger.info("Initializing DocumentFormatter.")
    return DocumentFormatter()

@lru_cache()
def get_prompt_service() -> PromptBase:
    """Get the prompt service instance based on environment configuration."""
    prompt_service_type = os.getenv("PROMPT_SERVICE_TYPE", "file")
    if prompt_service_type == "file":
        logger.info("Initializing FilePromptService.")
        return FilePromptService()
    else:
        raise ValueError(f"Unsupported PROMPT_SERVICE_TYPE: {prompt_service_type}")
