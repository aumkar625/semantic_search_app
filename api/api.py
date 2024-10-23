# api/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from typing import List, Optional
from summarization_module.summarization import summarize
import os

app = FastAPI()

# Initialize models and clients
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant_url = os.getenv('QDRANT_URL', 'http://qdrant:6333')
qdrant_client = QdrantClient(url=qdrant_url)

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    summarizer: Optional[str] = None  # Model name or API choice

class SearchResponse(BaseModel):
    documents: List[str]
    summary: str

@app.post('/search', response_model=SearchResponse)
async def search(request: SearchRequest):
    # Generate query embedding
    query_embedding = embedding_model.encode(request.query)

    # Perform the search
    search_result = qdrant_client.search(
        collection_name='squad_dataset_questions_answers',  # Updated collection name
        query_vector=query_embedding,
        limit=request.k
    )

    # Extract the documents
    docs = [hit.payload['text'] for hit in search_result]

    # Summarize the results
    summary = summarize(docs, request.summarizer)

    return SearchResponse(documents=docs, summary=summary)
