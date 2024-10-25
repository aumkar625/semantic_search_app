import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
import requests
import time
from requests.exceptions import HTTPError, RequestException

class QdrantUtils:
    def __init__(self, qdrant_url):
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.logger = logging.getLogger(__name__)

    def create_collection_if_not_exists(self, collection_name, vector_size, distance='Cosine'):
        """Check if collection exists; create if it does not."""
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

    def upload_documents(self, collection_name, documents, embeddings, file_path):
        """Upload documents and their embeddings to the specified collection."""
        try:
            # Prepare payload
            payload = [{'document_id': i + 1, 'text': doc, 'file_path': file_path} for i, doc in enumerate(documents)]

            # Upload documents to Qdrant
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

    def delete_records_by_filename(self, collection_name, file_path):
        """Deletes points from Qdrant collection based on file_path filter."""
        try:
            filter_query = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="file_path",
                        match=qdrant_models.MatchValue(value=file_path)
                    )
                ]
            )

            # Scroll through points matching the filter
            scroll_result = self.qdrant_client.scroll(
                collection_name=collection_name,
                filter=filter_query,
                limit=1,
                with_payload=False,
                with_vector=False
            )

            if not scroll_result.points:
                self.logger.info("No matching points found for deletion.")
                return False

            # Extract point IDs from the scroll result
            point_ids = [point.id for point in scroll_result.points]

            # Delete points by ID
            delete_result = self.qdrant_client.delete(
                collection_name=collection_name,
                points_selector=qdrant_models.PointsSelector(points=point_ids)
            )

            return delete_result.status == qdrant_models.UpdateStatus.COMPLETED

        except Exception as e:
            self.logger.error(f"Error during delete operation: {str(e)}")
            return False

    def delete_points_by_file_path(self,qdrant_url, collection_name, file_path, max_retries=3, backoff_factor=2):
        """Deletes points from Qdrant collection based on file_path filter using HTTP POST.

        Args:
        - qdrant_url (str): The base URL of the Qdrant instance.
        - collection_name (str): The name of the Qdrant collection.
        - file_path (str): The file path to filter points for deletion.
        - max_retries (int): Maximum number of retries for the request.
        - backoff_factor (int): Factor for exponential backoff (in seconds).

        Returns:
        - bool: True if deletion was successful, False otherwise.
        """
        scroll_url = f"{qdrant_url}/collections/{collection_name}/points/scroll"
        delete_url = f"{qdrant_url}/collections/{collection_name}/points/delete"

        # Payload for the scroll and delete request to find matching points
        search_payload = {
            "filter": {
                "must": [
                    {
                        "key": "file_path",
                        "match": {
                            "value": file_path
                        }
                    }
                ]
            },
            "limit": 1,
            "with_payload": False,
            "with_vector": False
        }

        delete_payload = {
            "filter": {
                "must": [
                    {
                        "key": "file_path",
                        "match": {
                            "value": file_path
                        }
                    }
                ]
            }
        }

        for attempt in range(1, max_retries + 1):
            try:
                # Scroll request to find point IDs
                response = requests.post(scroll_url, json=search_payload, timeout=10)
                response.raise_for_status()
                scroll_data = response.json()

                if not scroll_data.get("result", {}).get("points"):
                    self.logger.info("No matching points found for deletion.")
                    return False

                delete_response = requests.post(delete_url, json=delete_payload, timeout=10)
                delete_response.raise_for_status()

                # Log initial delete response
                delete_data = delete_response.json()
                operation_id = delete_data["result"]["operation_id"]
                status = delete_data["result"]["status"]

                # Log and return if the operation is acknowledged
                self.logger.info(f"Delete operation initiated. Operation ID: {operation_id}, Status: {status}")
                if status == "acknowledged":
                    self.logger.info(f"Delete operation for {file_path} successfully acknowledged.")
                    return True

                # If not acknowledged, retry or log failure
                self.logger.error(f"Unexpected delete status: {status}")
                return False

            except HTTPError as http_err:
                self.logger.error(f"HTTP error occurred on attempt {attempt}/{max_retries}: {http_err}")
            except RequestException as req_err:
                self.logger.error(f"Request exception occurred on attempt {attempt}/{max_retries}: {req_err}")
            except Exception as err:
                self.logger.error(f"Unexpected error on attempt {attempt}/{max_retries}: {err}")

            # Exponential backoff before retrying
            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                self.logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

        self.logger.error("Max retries exceeded. Deletion failed.")
        return False

    import requests
    import logging
    import time

    def get_document_count(self,collection_name, qdrant_url, max_retries=3, backoff_factor=2):
        """Fetch the document count for a specified collection with retry logic and exception handling."""
        self.logger.info(f"the url is {qdrant_url}")
        url = f"{qdrant_url}/collections/{collection_name}/points/count"

        headers = {"Content-Type": "application/json"}
        payload = {"exact": True}

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()

                # Extract count from JSON response
                count = response.json().get("result", {}).get("count", None)
                if count is not None:
                    logging.info(f"Collection '{collection_name}' document count: {count}")
                    return count
                else:
                    logging.error(f"Unable to fetch count for collection '{collection_name}': {response.json()}")
                    return 0

            except requests.exceptions.HTTPError as http_err:
                logging.error(f"HTTP error on attempt {attempt}/{max_retries}: {http_err}")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Request exception on attempt {attempt}/{max_retries}: {req_err}")
            except Exception as e:
                logging.error(f"Unexpected error on attempt {attempt}/{max_retries}: {e}")

            # Exponential backoff before retrying
            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

        logging.error("Max retries exceeded. Unable to fetch document count.")
        return 0


