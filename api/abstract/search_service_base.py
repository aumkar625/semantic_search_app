class SearchServiceBase:
    """Interface for search services."""

    def search(self, query_embedding, k: int):
        raise NotImplementedError("Search service must implement `search` method.")
