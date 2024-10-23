# app/__init__.py
from flask import Flask
import os

app = Flask(__name__)
app.config['API_URL'] = os.getenv('API_URL', 'http://localhost:8000')

from app import main
