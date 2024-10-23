# tests/test_app.py
from ui import app
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Semantic Search Engine' in response.data

def test_search_functionality(client):
    response = client.post('/', data={
        'query': 'artificial intelligence',
        'k': '3',
        'summarizer': 'facebook/bart-large-cnn'
    })
    assert response.status_code == 200
    assert b'Results for' in response.data
