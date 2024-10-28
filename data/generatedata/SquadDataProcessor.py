import os
import csv
from datasets import load_dataset
from math import ceil


class SquadDataProcessor:
    def __init__(self, output_dir="squad_csv_files", delimiter="|", num_files=20):
        """
        Initializes the SquadDataProcessor with specified parameters.

        Args:
        - output_dir (str): The directory to save CSV files.
        - delimiter (str): The delimiter to use in CSV files.
        - num_files (int): The number of CSV files to split the dataset into.
        """
        self.output_dir = output_dir
        self.delimiter = delimiter
        self.num_files = num_files

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def load_documents(self):
        """
        Loads the SQuAD dataset and processes it into a list of documents.

        Returns:
        - documents (list): A list of dictionaries containing context, question, and answer.
        """
        try:
            dataset = load_dataset('squad', split='train')
            documents = []

            for item in dataset:
                context = item['context']
                question = item['question']
                answer = item['answers']['text'][0]  # Taking the first answer

                # Combine the context, question, and answer into a single document
                document = {
                    'context': context,
                    'question': question,
                    'answer': answer
                }
                documents.append(document)

            return documents

        except Exception as e:
            print(f"Error loading SQuAD dataset: {str(e)}")
            return []

    def save_documents_to_csv(self):
        """
        Splits the dataset into parts and saves them as CSV files with unique document IDs.
        """
        try:
            documents = self.load_documents()
            if not documents:
                print("No documents loaded. Aborting save process.")
                return

            total_docs = len(documents)
            docs_per_file = ceil(total_docs / self.num_files)

            # Initialize document ID
            document_id = 1

            for i in range(self.num_files):
                start_index = i * docs_per_file
                end_index = min((i + 1) * docs_per_file, total_docs)

                # File name for each CSV file
                csv_file = os.path.join(self.output_dir, f"squad_part_{i + 1}.csv")

                # Write data to CSV with custom delimiter
                with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file, delimiter=self.delimiter)
                    writer.writerow(['Document_ID', 'Context', 'Question', 'Answer'])  # Header

                    for doc in documents[start_index:end_index]:
                        writer.writerow([document_id, doc['context'], doc['question'], doc['answer']])
                        document_id += 1  # Increment document ID for each record

            print(f"Saved {self.num_files} CSV files in '{self.output_dir}' with unique document IDs")

        except Exception as e:
            print(f"Error saving documents to CSV: {str(e)}")


# Example usage:
if __name__ == "__main__":
    # Create an instance of the class with default parameters
    processor = SquadDataProcessor()

    # Save the documents to CSV files
    processor.save_documents_to_csv()