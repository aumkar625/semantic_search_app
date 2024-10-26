# tests/test_api.py
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_search_endpoint():
    response = client.post('/search', json={'query': 'machine learning', 'k': 3})
    assert response.status_code == 200
    data = response.json()
    assert 'documents' in data
    assert 'summary' in data
    assert len(data['documents']) == 3
