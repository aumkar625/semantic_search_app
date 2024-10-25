import os
import csv
import logging
import time
from sentence_transformers import SentenceTransformer
from qdrant_utils import QdrantUtils  # Import only the QdrantUtils class


class FileUploaderToQdrant:
    def __init__(self, qdrant_url, mounted_dir, checklist_file="uploaded_files_checklist.txt"):
        self.qdrant_utils = QdrantUtils(qdrant_url)  # Initialize QdrantUtils
        self.qdrant_url = qdrant_url
        self.mounted_dir = mounted_dir
        self.checklist_file = os.path.join(mounted_dir + "log/", checklist_file)
        self.collection_name = os.getenv('TABLE')
        self.embedding_model = SentenceTransformer(os.environ["SENTENCE_TRANSFORMER"])
        self.files_location = os.path.join(mounted_dir, "files")

        # Setup logging
        log_file_path = os.path.join(mounted_dir, "log/service.log")
        logging.basicConfig(filename=log_file_path, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Ensure the checklist file exists
        if not os.path.exists(self.checklist_file):
            with open(self.checklist_file, 'w') as f:
                pass  # Create an empty file if it doesn't exist

        self.logger.info("Initialized FileUploaderToQdrant")

    def list_csv_files(self):
        """Lists all CSV files in the mounted directory."""
        try:
            files = [f for f in os.listdir(self.files_location) if f.endswith('.csv')]
            self.logger.info(f"Found {len(files)} CSV files in the mounted directory.")
            return files
        except Exception as e:
            self.logger.error(f"Error while listing CSV files: {str(e)}")
            return []

    def read_checklist(self):
        """Reads the checklist file to get the list of already uploaded files."""
        try:
            with open(self.checklist_file, 'r') as file:
                uploaded_files = {line.strip() for line in file.readlines()}
            self.logger.info(f"Read checklist with {len(uploaded_files)} files.")
            return uploaded_files
        except Exception as e:
            self.logger.error(f"Error while reading checklist file: {str(e)}")
            return set()

    def update_checklist(self, filename):
        """Adds a file to the checklist once it has been uploaded to Qdrant."""
        try:
            with open(self.checklist_file, 'a') as file:
                file.write(filename + '\n')
            self.logger.info(f"Updated checklist with file: {filename}")
        except Exception as e:
            self.logger.error(f"Error while updating checklist file: {str(e)}")

    def remove_from_checklist(self, filename):
        """Removes a file from the checklist if it no longer exists on the mounted directory."""
        try:
            uploaded_files = self.read_checklist()
            if filename in uploaded_files:
                uploaded_files.remove(filename)
                # Rewrite the checklist file
                with open(self.checklist_file, 'w') as file:
                    for file_name in uploaded_files:
                        file.write(file_name + '\n')
                self.logger.info(f"Removed {filename} from checklist.")
        except Exception as e:
            self.logger.error(f"Error while removing file from checklist: {str(e)}")

    def delete_from_qdrant(self, file_path):
        """Deletes records from Qdrant based on the file path and logs document counts."""
        try:
            # Get count before deletion
            count_before = self.qdrant_utils.get_document_count(self.collection_name, self.qdrant_url)
            self.logger.info(f"Document count before deletion: {count_before}")

            self.logger.info(f"Deleting records from Qdrant with file path: {file_path}")
            success = self.qdrant_utils.delete_points_by_file_path(self.qdrant_url, self.collection_name, file_path)
            if success:
                self.logger.info(f"Successfully deleted records for {file_path} from Qdrant.")
            else:
                self.logger.error(f"Failed to delete records for {file_path} from Qdrant.")

            # Delay of 1 second before getting the updated count
            time.sleep(1)

            # Get count after deletion
            count_after = self.qdrant_utils.get_document_count(self.collection_name, self.qdrant_url)
            self.logger.info(f"Document count after deletion: {count_after}")

        except Exception as e:
            self.logger.error(f"Error while deleting records from Qdrant: {str(e)}")

    def upload_file_to_qdrant(self, csv_file):
        """Uploads the contents of a CSV file to the Qdrant collection and logs document counts."""
        try:
            file_path = csv_file

            # Get count before uploading
            count_before = self.qdrant_utils.get_document_count(self.collection_name, self.qdrant_url)
            self.logger.info(f"Document count before upload: {count_before}")

            # Read CSV and generate document IDs
            documents, document_ids = [], []
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='|')
                for doc_id, row in enumerate(reader, start=1):
                    document = f"Context: {row['Context']}\nQuestion: {row['Question']}\nAnswer: {row['Answer']}"
                    documents.append(document)
                    document_ids.append(doc_id)

            self.logger.info(f"Read {len(documents)} documents from file: {csv_file}")

            # Generate embeddings
            embeddings = self.embedding_model.encode(documents, show_progress_bar=True)

            # Create collection if not exists
            self.qdrant_utils.create_collection_if_not_exists(self.collection_name, embeddings.shape[1])

            # Upload documents to Qdrant
            self.qdrant_utils.upload_documents(self.collection_name, documents, embeddings, file_path)
            self.logger.info(
                f"Successfully uploaded {len(documents)} documents to Qdrant collection: {self.collection_name}")

            # Delay of 1 second before getting the updated count
            time.sleep(1)

            # Get count after uploading
            count_after = self.qdrant_utils.get_document_count(self.collection_name, self.qdrant_url)
            self.logger.info(f"Document count after upload: {count_after}")

            # Update checklist
            self.update_checklist(os.path.basename(csv_file))

        except Exception as e:
            self.logger.error(f"Failed to upload {csv_file} to Qdrant: {str(e)}")

    def sync_files_with_qdrant(self):
        """Sync CSV files with Qdrant based on the checklist."""
        csv_files = set(self.list_csv_files())  # All files in the mounted directory
        uploaded_files = self.read_checklist()  # Files already uploaded to Qdrant

        # Files to upload
        files_to_upload = csv_files - uploaded_files

        # Files to delete
        files_to_delete = uploaded_files - csv_files

        # Upload new files
        for file in files_to_upload:
            csv_path = os.path.join(self.files_location, file)
            self.upload_file_to_qdrant(csv_path)

        # Delete files from Qdrant that are no longer in the directory
        for file in files_to_delete:
            csv_path = os.path.join(self.files_location, file)
            self.delete_from_qdrant(csv_path)
            self.remove_from_checklist(file)

    def manual_trigger_sync(self):
        """Manually triggers the sync operation."""
        self.sync_files_with_qdrant()

if __name__ == "__main__":
    # Get environment variables or set defaults
    qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
    mounted_dir = "/mnt/data/"  # Ensure this path is where your CSV files are mounted

    # Initialize the FileUploaderToQdrant
    uploader = FileUploaderToQdrant(qdrant_url=qdrant_url, mounted_dir=mounted_dir)

    # Manual trigger for syncing files with Qdrant
    uploader.manual_trigger_sync()
