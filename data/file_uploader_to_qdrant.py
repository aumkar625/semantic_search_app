# data/file_uploader_to_qdrant.py

import os
import csv
import logging
import time
from sentence_transformers import SentenceTransformer
from qdrant_utils import QdrantUtils  # Import only the QdrantUtils class


class FileUploaderToQdrant:
    def __init__(self, qdrant_url, mounted_dir, qdrant_api_key, checklist_file="uploaded_files_checklist.txt"):
        self.qdrant_utils = QdrantUtils(qdrant_url,qdrant_api_key)
        self.qdrant_url = qdrant_url
        self.mounted_dir = mounted_dir
        self.checklist_file = os.path.join(mounted_dir, "log", checklist_file)
        self.collection_name = os.getenv('TABLE')
        self.qdrant_api_key= os.getenv('QDRANT_API_KEY')

        try:
            self.embedding_model = SentenceTransformer(os.environ["SENTENCE_TRANSFORMER"])
        except Exception as e:
            raise RuntimeError("Failed to initialize SentenceTransformer model") from e

        self.files_location = os.path.join(mounted_dir, "files")
        log_file_path = os.path.join(mounted_dir, "log", "service.log")
        logging.basicConfig(filename=log_file_path, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        if not os.path.exists(self.checklist_file):
            open(self.checklist_file, 'w').close()  # Create an empty file if it doesn't exist

        self.logger.info("Initialized FileUploaderToQdrant")

    def list_csv_files(self):
        """Lists all CSV files in the mounted directory."""
        try:
            files = [f for f in os.listdir(self.files_location) if f.endswith('.csv')]
            self.logger.info(f"Found {len(files)} CSV files in the mounted directory.")
            return files
        except Exception as e:
            self.logger.error(f"Error listing CSV files: {str(e)}")
            return []

    def read_checklist(self):
        """Reads the checklist file to get the list of already uploaded files."""
        try:
            with open(self.checklist_file, 'r') as file:
                uploaded_files = {line.strip() for line in file.readlines()}
            self.logger.info(f"Read checklist with {len(uploaded_files)} files.")
            return uploaded_files
        except Exception as e:
            self.logger.error(f"Error reading checklist file: {str(e)}")
            return set()

    def update_checklist(self, filename):
        """Adds a file to the checklist once uploaded to Qdrant."""
        try:
            with open(self.checklist_file, 'a') as file:
                file.write(filename + '\n')
            self.logger.info(f"Updated checklist with file: {filename}")
        except Exception as e:
            self.logger.error(f"Error updating checklist file: {str(e)}")

    def remove_from_checklist(self, filename):
        """Removes a file from the checklist if it no longer exists in the mounted directory."""
        try:
            uploaded_files = self.read_checklist()
            if filename in uploaded_files:
                uploaded_files.remove(filename)
                with open(self.checklist_file, 'w') as file:
                    for file_name in uploaded_files:
                        file.write(file_name + '\n')
                self.logger.info(f"Removed {filename} from checklist.")
        except Exception as e:
            self.logger.error(f"Error removing file from checklist: {str(e)}")

    def delete_from_qdrant(self, file_path):
        """Deletes records from Qdrant based on the file path and logs document counts."""
        try:
            count_before = self.qdrant_utils.get_document_count(self.collection_name,self.qdrant_api_key)
            self.logger.info(f"Document count before deletion: {count_before}")

            self.logger.info(f"Deleting records from Qdrant with file path: {file_path}")
            success = self.qdrant_utils.delete_points_by_file_path( self.collection_name, file_path, self.qdrant_api_key)
            if success:
                self.logger.info(f"Successfully deleted records for {file_path} from Qdrant.")
            else:
                self.logger.error(f"Failed to delete records for {file_path} from Qdrant.")

            time.sleep(1)
            count_after = self.qdrant_utils.get_document_count(self.collection_name, self.qdrant_api_key)
            self.logger.info(f"Document count after deletion: {count_after}")

        except Exception as e:
            self.logger.error(f"Error deleting records from Qdrant: {str(e)}")

    def upload_file_to_qdrant(self, csv_file):
        """Uploads the contents of a CSV file to the Qdrant collection and logs document counts."""
        try:
            count_before = self.qdrant_utils.get_document_count(self.collection_name, self.qdrant_api_key)
            self.logger.info(f"Document count before upload: {count_before}")

            documents, document_ids = [], []
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='|')
                for doc_id, row in enumerate(reader, start=1):
                    document = f"Context: {row['Context']}\nQuestion: {row['Question']}\nAnswer: {row['Answer']}"
                    documents.append(document)
                    document_ids.append(doc_id)

            self.logger.info(f"Read {len(documents)} documents from file: {csv_file}")

            embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
            self.qdrant_utils.create_collection_if_not_exists(self.collection_name, embeddings.shape[1])
            self.qdrant_utils.upload_documents(self.collection_name, documents, embeddings, csv_file)
            self.logger.info(f"Uploaded {len(documents)} documents to Qdrant collection: {self.collection_name}")

            time.sleep(1)
            count_after = self.qdrant_utils.get_document_count(self.collection_name,self.qdrant_api_key)
            self.logger.info(f"Document count after upload: {count_after}")

            self.update_checklist(os.path.basename(csv_file))

        except Exception as e:
            self.logger.error(f"Error uploading {csv_file} to Qdrant: {str(e)}")

    def sync_files_with_qdrant(self):
        """Sync CSV files with Qdrant based on the checklist."""
        try:
            csv_files = set(self.list_csv_files())
            uploaded_files = self.read_checklist()

            files_to_upload = csv_files - uploaded_files
            files_to_delete = uploaded_files - csv_files

            for file in files_to_upload:
                csv_path = os.path.join(self.files_location, file)
                self.upload_file_to_qdrant(csv_path)

            for file in files_to_delete:
                csv_path = os.path.join(self.files_location, file)
                self.delete_from_qdrant(csv_path)
                self.remove_from_checklist(file)

        except Exception as e:
            self.logger.error(f"Error syncing files with Qdrant: {str(e)}")

    def manual_trigger_sync(self):
        """Manually triggers the sync operation."""
        try:
            self.sync_files_with_qdrant()
        except Exception as e:
            self.logger.error(f"Error during manual sync: {str(e)}")


if __name__ == "__main__":
    qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
    qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
    mounted_dir = "/mnt/data/"

    uploader = FileUploaderToQdrant(qdrant_url=qdrant_url, mounted_dir=mounted_dir,qdrant_api_key=qdrant_api_key)
    uploader.manual_trigger_sync()
