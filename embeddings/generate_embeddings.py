# embeddings/generate_embeddings.py
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from data.load_data import load_documents
import os

def generate_and_upload_embeddings():
    # Load documents
    documents = load_documents()

    # Initialize the embedding model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embeddings
    embeddings = embedding_model.encode(documents, show_progress_bar=True)

    # Initialize Qdrant client
    qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
    qdrant_client = QdrantClient(url=qdrant_url)

    # Define a collection in Qdrant
    qdrant_client.recreate_collection(
        collection_name='newsgroups',
        vectors_config=qdrant_models.VectorParams(size=embeddings.shape[1], distance='Cosine')
    )

    # Upload documents and embeddings
    qdrant_client.upload_collection(
        collection_name='newsgroups',
        vectors=embeddings,
        payload=[{'text': doc} for doc in documents],
        ids=None,
        batch_size=64
    )

if __name__ == "__main__":
    generate_and_upload_embeddings()
