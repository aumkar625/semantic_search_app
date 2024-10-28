# services/sentence_transformer_service.py

import logging
import os
import asyncio

from sentence_transformers import SentenceTransformer
from abstract.embedding_base import EmbeddingServiceBase
import services.logger_base  # Ensure logging is configured

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddingService(EmbeddingServiceBase):
    """Service for generating embeddings using SentenceTransformer."""

    def __init__(self):
        model_name = os.getenv("SENTENCE_TRANSFORMER", "default-model-name")
        cache_folder = os.getenv("TRANSFORMERS_CACHE", "/tmp/cache")
        self.model = SentenceTransformer(model_name, cache_folder=cache_folder)
        logger.info(f"SentenceTransformer model initialized with model: {model_name}")

    async def generate_embedding(self, text: str):
        """Generates an embedding for the given text."""
        try:
            embedding = await asyncio.to_thread(self.model.encode, text)
            logger.debug("Generated embedding for text.")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            raise