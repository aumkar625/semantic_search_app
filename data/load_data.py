# data/load_data.py
from sklearn.datasets import fetch_20newsgroups

def load_documents():
    newsgroups = fetch_20newsgroups(subset='all')
    documents = newsgroups.data
    return documents
