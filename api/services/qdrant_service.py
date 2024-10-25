import os
import logging
from abstract.vector_db_base import VectorDBBase
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

class QdrantService(VectorDBBase):
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        self.client = QdrantClient(url=qdrant_url)
        logger.info("Qdrant client initialized.")

    def search(self, query_embedding, k: int):
        return self.client.search(
            collection_name=os.getenv('TABLE'),
            query_vector=query_embedding,
            limit=k
        )

