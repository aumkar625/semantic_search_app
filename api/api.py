# api/api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ApiException, ResponseHandlingException, UnexpectedResponse
from typing import List, Optional
from summarization_module.summarization import summarize
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",  # React frontend
    "http://localhost:80",  # If frontend runs on port 80
    # Add other origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Update this as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models and clients
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("SentenceTransformer model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model: {e}")
    raise e  # Exit if the model cannot be loaded

# Initialize Qdrant client
qdrant_client = None
try:
    qdrant_url = os.getenv('QDRANT_URL')  # Use service name 'qdrant' as per Docker Compose
    qdrant_client = QdrantClient(url=qdrant_url)
    logger.info(f"Connected to Qdrant at {qdrant_url}.")
    count=qdrant_client.count("squad_dataset_questions_answers")
    logger.info(f"number of records on Qdrant at {count}.")
except ApiException as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    raise HTTPException(status_code=500, detail="Failed to connect to the vector database.")
except Exception as e:
    logger.error(f"Unexpected error when connecting to Qdrant: {e}")
    raise HTTPException(status_code=500, detail="An unexpected error occurred while connecting to the vector database.")


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    summarizer: Optional[str] = None  # Model name or API choice

    @validator('k')
    def k_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('k must be a positive integer')
        return v

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('query must not be empty')
        return v


class SearchResponse(BaseModel):
    documents: List[str]
    summary: Optional[str] = None


@app.post('/api/search', response_model=SearchResponse)
async def search(request: SearchRequest):
    if not qdrant_client:
        logger.error("Qdrant client is not initialized.")
        raise HTTPException(status_code=500, detail="Vector database client is not available.")

    try:
        logger.info(f"Received search request: Query='{request.query}', Top K={request.k}")

        # Generate query embedding
        query_embedding = embedding_model.encode(request.query)
        logger.info("Query embedding generated successfully.")
    except Exception as e:
        logger.error(f"Error generating query embedding: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate query embedding.")

    try:
        # Perform the search
        search_result = qdrant_client.search(
            collection_name='squad_dataset_questions_answers',  # Updated collection name
            query_vector=query_embedding,
            limit=request.k
        )
        logger.info(f"Search completed. Retrieved {len(search_result)} documents.")
    except (ResponseHandlingException, UnexpectedResponse) as e:
        logger.error(f"Qdrant search error: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while searching the vector database.")
    except ApiException as e:
        logger.error(f"Qdrant API exception during search: {e}")
        raise HTTPException(status_code=500, detail="API error occurred while searching the vector database.")
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the search.")

    try:
        # Extract the documents
        docs = [hit.payload.get('text', '') for hit in search_result]
        logger.info(f"Extracted {len(docs)} documents from search results.")
    except Exception as e:
        logger.error(f"Error extracting documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract documents from search results.")

    summary = ''
    if request.summarizer:
        try:
            # Summarize the results
            summary = summarize(docs, request.summarizer).text
            logger.info(f"Summary generated successfully {summary}.")
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            # Depending on requirements, you can choose to fail the request or proceed without summary
            raise HTTPException(status_code=500, detail="Failed to generate summary.")
    return SearchResponse(documents=docs, summary=summary)
