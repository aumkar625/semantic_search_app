from abstract.search_service_base import SearchServiceBase
from services.service_factory import get_vector_db_service, get_embedding_service

class SearchService(SearchServiceBase):
    def __init__(self):
        self.vector_db_service = get_vector_db_service()
        self.embedding_service = get_embedding_service()

    def search(self, query_embedding, k: int):
        return self.vector_db_service.search(query_embedding, k)
