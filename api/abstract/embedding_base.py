class EmbeddingServiceBase:
    """Interface for embedding services."""
    
    def generate_embedding(self, text: str):
        raise NotImplementedError("Embedding service must implement `generate_embedding` method.")

