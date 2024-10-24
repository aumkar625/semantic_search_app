# data/generate_embeddings.py
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

    # Generate data
    embeddings = embedding_model.encode(documents, show_progress_bar=True)

    # Initialize Qdrant client
    qdrant_url = os.getenv('QDRANT_URL', 'http://qdrant:6333')
    qdrant_client = QdrantClient(url=qdrant_url)

    # Define a collection in Qdrant
    qdrant_client.recreate_collection(
        collection_name='squad_dataset_questions_answers',
        vectors_config=qdrant_models.VectorParams(size=embeddings.shape[1], distance='Cosine')
    )

    # Upload documents and data
    qdrant_client.upload_collection(
        collection_name='squad_dataset_questions_answers',
        vectors=embeddings,
        payload=[{'text': doc} for doc in documents],
        ids=None,
        batch_size=64
    )


import csv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

# Generate data using a pre-trained model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def upload_csv_to_qdrant(input_dir, csv_file, qdrant_client, collection_name):
    """
    Reads a CSV file, generates data, and uploads the data to Qdrant with document_id and file path.
    If the collection exists, it will use the existing collection; otherwise, it will create the collection.

    Args:
    - input_dir (str): Path to the directory containing the file.
    - csv_file (str): The name of the CSV file to be uploaded.
    - qdrant_client (QdrantClient): The Qdrant client instance.
    - collection_name (str): The Qdrant collection name to upload the data.
    """
    file_path = os.path.join(input_dir, csv_file)

    try:
        # Read the CSV file and generate document IDs
        documents = []
        document_ids = []  # Store document_id for each row
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='|')
            doc_id = 1
            for row in reader:
                document = (
                    f"\nContext: {row['Context']}\n"f"Question: {row['Question']}\n"f"Answer: {row['Answer']}\n")
                documents.append(document)
                document_ids.append(doc_id)
                doc_id += 1

        print(f"Read {len(documents)} documents from file: {csv_file}")

        embeddings = embedding_model.encode(documents, show_progress_bar=True)

        # Check if the collection exists in Qdrant
        collections = qdrant_client.get_collections().collections
        existing_collections = [col.name for col in collections]

        if collection_name not in existing_collections:
            # Collection doesn't exist, create it
            print(f"Collection '{collection_name}' does not exist. Creating new collection...")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=qdrant_models.VectorParams(size=embeddings.shape[1], distance='Cosine')
            )
        else:
            print(f"Collection '{collection_name}' already exists. Using the existing collection.")

        # Prepare payload with document_id, text, and file path
        payload = [{'document_id': doc_id, 'text': doc, 'file_path': file_path}
                   for doc_id, doc in zip(document_ids, documents)]

        # Upload the documents and their data to Qdrant
        qdrant_client.upload_collection(
            collection_name=collection_name,
            vectors=embeddings,
            payload=payload,
            ids=None,
            batch_size=64
        )

        print(f"Successfully uploaded {len(documents)} documents to Qdrant collection: {collection_name}")

    except Exception as e:
        print(f"Error while uploading file {csv_file} to Qdrant: {str(e)}")


if __name__ == "__main__":
    generate_and_upload_embeddings()
