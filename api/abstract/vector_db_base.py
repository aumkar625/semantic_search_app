from typing import List

class VectorDBBase:
    """Interface for vector database services."""
    
    def search(self, query_embedding, k: int) -> List[dict]:
        raise NotImplementedError("Vector database service must implement `search` method.")

