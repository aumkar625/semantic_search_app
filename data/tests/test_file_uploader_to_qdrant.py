# tests/test_file_uploader_to_qdrant.py

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
from app.file_uploader_to_qdrant import FileUploaderToQdrant

class TestFileUploaderToQdrant(unittest.TestCase):
    def setUp(self):
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.mounted_dir = '/mnt/data/'
        self.uploader = FileUploaderToQdrant(self.qdrant_url, self.mounted_dir)

    @patch('os.listdir')
    def test_list_csv_files(self, mock_listdir):
        mock_listdir.return_value = ['file1.csv', 'file2.csv', 'file3.txt']
        files = self.uploader.list_csv_files()
        self.assertEqual(files, ['file1.csv', 'file2.csv'])

    @patch('builtins.open', new_callable=mock_open, read_data='file1.csv\nfile2.csv\n')
    def test_read_checklist(self, mock_file):
        uploaded_files = self.uploader.read_checklist()
        self.assertEqual(uploaded_files, {'file1.csv', 'file2.csv'})

    @patch('builtins.open', new_callable=mock_open)
    def test_update_checklist(self, mock_file):
        self.uploader.update_checklist('file3.csv')
        mock_file.assert_called_with(self.uploader.checklist_file, 'a')
        mock_file().write.assert_called_with('file3.csv\n')

    @patch('builtins.open', new_callable=mock_open, read_data='file1.csv\nfile2.csv\n')
    def test_remove_from_checklist(self, mock_file):
        with patch.object(self.uploader, 'read_checklist', return_value={'file1.csv', 'file2.csv'}):
            self.uploader.remove_from_checklist('file1.csv')
            mock_file.assert_called_with(self.uploader.checklist_file, 'w')
            mock_file().write.assert_called_with('file2.csv\n')

    @patch('file_uploader_to_qdrant.QdrantUtils')
    @patch('file_uploader_to_qdrant.SentenceTransformer')
    def test_upload_file_to_qdrant(self, mock_sentence_transformer, mock_qdrant_utils):
        # Mock the embedding model
        mock_model_instance = mock_sentence_transformer.return_value
        mock_model_instance.encode.return_value = [[0.1, 0.2, 0.3]]

        # Mock the Qdrant utils
        mock_qdrant_instance = mock_qdrant_utils.return_value
        mock_qdrant_instance.get_document_count.return_value = 0

        # Mock reading the CSV file
        csv_content = 'Context|Question|Answer\nThis is context|This is question|This is answer\n'
        with patch('builtins.open', new_callable=mock_open, read_data=csv_content):
            with patch('csv.DictReader', return_value=[{'Context': 'This is context', 'Question': 'This is question', 'Answer': 'This is answer'}]):
                self.uploader.upload_file_to_qdrant('/mnt/data/files/file1.csv')

        # Assertions
        mock_model_instance.encode.assert_called_once()
        mock_qdrant_instance.upload_documents.assert_called_once()

    # Additional tests can be added for other methods

if __name__ == '__main__':
    unittest.main()
