# ui/__init__.py
from flask import Flask
import os

app = Flask(__name__)
app.config['API_URL'] = os.getenv('API_URL', 'http://api:8000')

# Import and register the blueprint
from ui.main import main_bp
app.register_blueprint(main_bp)
