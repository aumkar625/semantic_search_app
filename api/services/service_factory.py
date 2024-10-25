import os
from services.qdrant_service import QdrantService
from services.sentence_transformer_service import SentenceTransformerEmbeddingService
from services.summarization_service import SummarizationService
from services.document_formatter import DocumentFormatter
from abstract.vector_db_base import VectorDBBase
from abstract.embedding_base import EmbeddingServiceBase
from abstract.summarization_base import SummarizationBase


def get_vector_db_service() -> VectorDBBase:
    """Get the vector database service instance based on environment configuration."""
    db_type = os.getenv("VECTOR_DB_TYPE", "qdrant")
    if db_type == "qdrant":
        return QdrantService()
    else:
        raise ValueError(f"Unsupported VECTOR_DB_TYPE: {db_type}")


def get_embedding_service() -> EmbeddingServiceBase:
    """Get the embedding service instance."""
    embedding_type = os.getenv("EMBEDDING_SERVICE_TYPE", "sentence_transformer")
    if embedding_type == "sentence_transformer":
        return SentenceTransformerEmbeddingService()
    else:
        raise ValueError(f"Unsupported EMBEDDING_SERVICE_TYPE: {embedding_type}")


def get_summarization_service() -> SummarizationBase:
    """Get the summarization service instance."""
    summarizer_type = os.getenv("SUMMARIZATION_SERVICE_TYPE", "default")
    if summarizer_type == "default":
        return SummarizationService()
    else:
        raise ValueError(f"Unsupported SUMMARIZATION_SERVICE_TYPE: {summarizer_type}")


# Aliases for search and format services to align with naming convention
def get_search_service() -> VectorDBBase:
    """Alias for get_vector_db_service to provide search service."""
    return get_vector_db_service()


def get_format_service() -> EmbeddingServiceBase:
    """Alias for get_embedding_service to provide format service."""
    return DocumentFormatter()
