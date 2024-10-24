from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, QdrantClientException


class QdrantUtils:
    def __init__(self):
        try:
            # Load the pre-trained embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
            raise

    def search_with_text(self, query_text, qdrant_client, collection_name, top_k=5):
        """
        Generates an embedding for the input text and performs a vector search in Qdrant.

        Args:
        - query_text (str): The input text to search for.
        - qdrant_client (QdrantClient): The Qdrant client instance.
        - collection_name (str): The Qdrant collection name to search within.
        - top_k (int): The number of top results to return (default is 5).

        Returns:
        - list: A list of search results with document payloads.
        """
        try:
            if not query_text or not isinstance(query_text, str):
                raise ValueError("Invalid query text. It should be a non-empty string.")

            # Generate an embedding for the query text
            query_embedding = self.embedding_model.encode([query_text])

            # Perform the search in Qdrant using the generated embedding
            search_result = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding[0],  # Use the first vector in the array
                limit=top_k,  # Return top K results
                with_payload=True  # Retrieve payloads (e.g., text, document_id, file_path)
            )

            return search_result

        except ValueError as ve:
            print(f"Value error during search: {str(ve)}")
        except QdrantClientException as qe:
            print(f"Qdrant client error: {str(qe)}")
        except Exception as e:
            print(f"Unexpected error during search: {str(e)}")
            raise

    def search(self, qdrant_client, collection_name, query_text):
        """
        Wrapper method to perform a search and print results.
        """
        try:
            results = self.search_with_text(query_text, qdrant_client, collection_name, top_k=5)

            # Check if results exist before trying to print
            if not results:
                print("No results found.")
                return

            # Print the search results
            for i, result in enumerate(results):
                print(f"Result {i + 1}:")
                print(f"Score: {result.score}")
                print(f"Document ID: {result.payload.get('document_id')}")
                print(f"File Path: {result.payload.get('file_path')}")
                print(f"Text: {result.payload.get('text')}")
                print()

        except Exception as e:
            print(f"Error during search operation: {str(e)}")

    def delete_records_by_filename(self, qdrant_client, collection_name, file_path):
        """
        Deletes records from a Qdrant collection where the file_path matches the given filename.

        Args:
        - qdrant_client (QdrantClient): The Qdrant client instance.
        - collection_name (str): The name of the collection to delete records from.
        - file_path (str): The file path (or filename) to match for deletion.
        """
        try:
            if not file_path or not isinstance(file_path, str):
                raise ValueError("Invalid file path. It should be a non-empty string.")

            # Define the filter based on the file_path in the payload
            filter_query = {
                "must": [
                    {
                        "key": "file_path",
                        "match": {
                            "value": file_path
                        }
                    }
                ]
            }

            # Perform the deletion
            qdrant_client.delete(
                collection_name=collection_name,
                filter=filter_query
            )

            print(
                f"Records with file_path '{file_path}' have been successfully deleted from '{collection_name}' collection.")

        except ValueError as ve:
            print(f"Value error during deletion: {str(ve)}")
        except QdrantClientException as qe:
            print(f"Qdrant client error during deletion: {str(qe)}")
        except Exception as e:
            print(f"Unexpected error during deletion: {str(e)}")

    def count_collection(self, qdrant_client, collection_name):
        """
        Returns the total count of records in a given collection.

        Args:
        - qdrant_client (QdrantClient): The Qdrant client instance.
        - collection_name (str): The name of the collection to count records.

        Returns:
        - int: Total count of records in the collection.
        """
        try:
            if not collection_name or not isinstance(collection_name, str):
                raise ValueError("Invalid collection name. It should be a non-empty string.")

            collection_info = qdrant_client.get_collection(collection_name)
            count = qdrant_client.count(collection_name)

            return count

        except ValueError as ve:
            print(f"Value error during count: {str(ve)}")
        except QdrantClientException as qe:
            print(f"Qdrant client error during count: {str(qe)}")
        except Exception as e:
            print(f"Unexpected error during count operation: {str(e)}")
            return None