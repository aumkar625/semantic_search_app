# data/qdrant_utils.py

import logging
import requests
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from requests.exceptions import HTTPError, RequestException

class QdrantUtils:
    def __init__(self, qdrant_url, qdrant_api_key):
        self.qdrant_url = qdrant_url
        self.qdrant_api_key = qdrant_api_key
        self.qdrant_client = QdrantClient(url=qdrant_url,api_key=qdrant_api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"the args are {self.qdrant_url},{self.qdrant_api_key}")

    def create_collection_if_not_exists(self, collection_name, vector_size, distance='Cosine'):
        """Creates a collection in Qdrant if it does not exist."""
        try:
            collections = self.qdrant_client.get_collections().collections
            existing_collections = [col.name for col in collections]

            if collection_name not in existing_collections:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qdrant_models.VectorParams(size=vector_size, distance=distance)
                )
                self.logger.info(f"Created collection '{collection_name}' with vector size {vector_size}.")
            else:
                self.logger.info(f"Collection '{collection_name}' already exists.")
        except Exception as e:
            self.logger.error(f"Error creating collection '{collection_name}': {str(e)}")
            raise  # Re-raise exception for external handling if required

    def upload_documents(self, collection_name, documents, embeddings, file_path):
        """Uploads documents and their embeddings to the specified collection."""
        try:
            payload = [{'document_id': i + 1, 'text': doc, 'file_path': file_path} for i, doc in enumerate(documents)]

            result = self.qdrant_client.upload_collection(
                collection_name=collection_name,
                vectors=embeddings,
                payload=payload,
                ids=None,
                batch_size=64
            )
            self.logger.info(f"Uploaded {len(documents)} documents to collection '{collection_name}' from file {file_path}.")
            return result
        except Exception as e:
            self.logger.error(f"Error uploading documents to collection '{collection_name}': {str(e)}")
            raise

    def delete_points_by_file_path(self, collection_name, file_path, api_key, max_retries=3, backoff_factor=2):
        """Deletes points from a Qdrant collection based on file_path filter using HTTP POST."""
        scroll_url = f"{self.qdrant_url}/collections/{collection_name}/points/scroll"
        delete_url = f"{self.qdrant_url}/collections/{collection_name}/points/delete"
        headers = {"Content-Type": "application/json", "api-key": api_key}
        search_payload = {
            "filter": {
                "must": [
                    {"key": "file_path", "match": {"value": file_path}}
                ]
            },
            "limit": 1,
            "with_payload": False,
            "with_vector": False
        }
        delete_payload = {
            "filter": {
                "must": [
                    {"key": "file_path", "match": {"value": file_path}}
                ]
            }
        }

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(scroll_url, headers=headers, json=search_payload, timeout=10)
                response.raise_for_status()
                scroll_data = response.json()

                if not scroll_data.get("result", {}).get("points"):
                    self.logger.info("No matching points found for deletion.")
                    return False

                delete_response = requests.post(delete_url, json=delete_payload, timeout=10)
                delete_response.raise_for_status()

                delete_data = delete_response.json()
                operation_id = delete_data["result"]["operation_id"]
                status = delete_data["result"]["status"]

                self.logger.info(f"Delete operation initiated. Operation ID: {operation_id}, Status: {status}")
                if status == "acknowledged":
                    self.logger.info(f"Delete operation for {file_path} successfully acknowledged.")
                    return True

                self.logger.error(f"Unexpected delete status: {status}")
                return False

            except HTTPError as http_err:
                self.logger.error(f"HTTP error on attempt {attempt}/{max_retries}: {http_err}")
            except RequestException as req_err:
                self.logger.error(f"Request exception on attempt {attempt}/{max_retries}: {req_err}")
            except Exception as err:
                self.logger.error(f"Unexpected error on attempt {attempt}/{max_retries}: {err}")

            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                self.logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

        self.logger.error("Max retries exceeded. Deletion failed.")
        return False

    def get_document_count(self, collection_name, api_key, max_retries=3, backoff_factor=2):
        """Fetch the document count for a specified collection with retry logic and exception handling."""
        url = f"{self.qdrant_url}/collections/{collection_name}/points/count"
        headers = {"Content-Type": "application/json", "api-key": api_key}
        payload = {"exact": True}

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()

                count = response.json().get("result", {}).get("count", 0)
                self.logger.info(f"Collection '{collection_name}' document count: {count}")
                return count

            except HTTPError as http_err:
                self.logger.error(f"HTTP error on attempt {attempt}/{max_retries}: {http_err}")
            except RequestException as req_err:
                self.logger.error(f"Request exception on attempt {attempt}/{max_retries}: {req_err}")
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt}/{max_retries}: {e}")

            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                self.logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

        self.logger.error("Max retries exceeded. Unable to fetch document count.")
        return 0
