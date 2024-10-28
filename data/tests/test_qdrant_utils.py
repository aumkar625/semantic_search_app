# tests/test_qdrant_utils.py

import unittest
from unittest.mock import MagicMock, patch
from app.qdrant_utils import QdrantUtils
import os
import numpy as np

class TestQdrantUtils(unittest.TestCase):
    def setUp(self):
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.utils = QdrantUtils(self.qdrant_url)
        self.embeddings = np.linspace(0.10, 0.40, 300)

    @patch('qdrant_utils.QdrantClient')
    def test_2_create_collection_if_not_exists(self, mock_qdrant_client):
        mock_client_instance = mock_qdrant_client.return_value
        mock_client_instance.has_collection.return_value = False

        self.utils.create_collection_if_not_exists('test_collection', 300)
        mock_client_instance.create_collection.assert_called_once()

    @patch('qdrant_utils.QdrantClient')
    def test_3_upload_documents(self, mock_qdrant_client):
        mock_client_instance = mock_qdrant_client.return_value

        documents = ['doc1']
        embeddings = self.embeddings
        file_path = '/path/to/file.csv'
        self.utils.upload_documents('test_collection', documents, embeddings, file_path)
        mock_client_instance.upload_collection.assert_called_once()

    @patch('qdrant_utils.QdrantClient')
    def test_1_delete_points_by_file_path(self, mock_qdrant_client):
        mock_client_instance = mock_qdrant_client.return_value
        mock_delete_result = MagicMock()
        mock_delete_result.status = 'completed'
        mock_client_instance.delete.return_value = mock_delete_result

        result = self.utils.delete_points_by_file_path(self.qdrant_url,'test_collection', '/path/to/file.csv')
        self.assertTrue(result)
        mock_client_instance.delete.assert_called_once()

    @patch('qdrant_utils.QdrantClient')
    def test_4_get_document_count(self, mock_qdrant_client):
        mock_client_instance = mock_qdrant_client.return_value
        mock_count_result = MagicMock()
        mock_count_result.count = 1
        mock_client_instance.count.return_value = mock_count_result

        count = self.utils.get_document_count('test_collection')
        self.assertEqual(count, 1)
        mock_client_instance.count.assert_called_once()

if __name__ == '__main__':
    unittest.main()