import os
import logging
from sentence_transformers import SentenceTransformer
from abstract.embedding_base import EmbeddingServiceBase

logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddingService(EmbeddingServiceBase):
    def __init__(self):
        model_name = os.getenv("SENTENCE_TRANSFORMER")
        self.model = SentenceTransformer(model_name)
        logger.info("SentenceTransformer model initialized.")

    def generate_embedding(self, text: str):
        return self.model.encode(text)

