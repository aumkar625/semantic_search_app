import os
import csv
from qdrant_utils import QdrantUtils  # Assuming QdrantUtils is already implemented
from time import sleep


class FileUploaderToQdrant:
    def __init__(self, qdrant_url, mounted_dir, collection_name="squad_dataset"):
        """
        Initializes the FileUploaderToQdrant with necessary parameters.

        Args:
        - qdrant_url (str): The URL of the Qdrant service.
        - mounted_dir (str): The directory where files will be mounted.
        - collection_name (str): The Qdrant collection name to upload the data into.
        """
        self.qdrant_utils = QdrantUtils(qdrant_url)  # Use the existing QdrantUtils class
        self.mounted_dir = mounted_dir
        self.collection_name = collection_name

    def list_csv_files(self):
        """
        Lists all CSV files in the mounted directory.

        Returns:
        - List of CSV files in the directory.
        """
        try:
            files = [f for f in os.listdir(self.mounted_dir) if f.endswith('.csv')]
            return files
        except Exception as e:
            print(f"Error while listing CSV files: {str(e)}")
            return []

    def upload_files_to_qdrant(self):
        """
        Uploads the contents of all CSV files in the mounted directory to Qdrant.
        """
        csv_files = self.list_csv_files()

        if not csv_files:
            print("No CSV files found in the mounted directory.")
            return

        for csv_file in csv_files:
            csv_path = os.path.join(self.mounted_dir, csv_file)
            self.upload_file_to_qdrant(csv_path)

    def upload_file_to_qdrant(self, csv_file):
        """
        Uploads the contents of a CSV file to the Qdrant collection.

        Args:
        - csv_file (str): The path to the CSV file to upload.
        """
        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='|')

                for row in reader:
                    context = row['Context']
                    question = row['Question']
                    answer = row['Answer']
                    document = f"Context: {context}\nQuestion: {question}\nAnswer: {answer}"

                    # Use the existing QdrantUtils class to upload
                    self.qdrant_utils.upload_document_to_qdrant(self.collection_name, document)

            print(f"Successfully uploaded data from {csv_file} to Qdrant collection '{self.collection_name}'.")

        except Exception as e:
            print(f"Failed to upload {csv_file} to Qdrant: {str(e)}")

    def manual_trigger_upload(self):
        """
        Manually trigger the upload process for all CSV files in the mounted directory.
        """
        input("Press Enter to trigger the CSV upload process...")
        self.upload_files_to_qdrant()


if __name__ == "__main__":
    # Get environment variables or set defaults
    qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
    mounted_dir = "/mnt/data"

    # Initialize the FileUploaderToQdrant
    uploader = FileUploaderToQdrant(qdrant_url=qdrant_url, mounted_dir=mounted_dir)

    # Wait for manual triggering
    while True:
        uploader.manual_trigger_upload()
        print("Waiting for next manual trigger...")
        sleep(5)  # You can adjust this sleep interval to your needs
