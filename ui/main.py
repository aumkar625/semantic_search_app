# ui/main.py
from flask import Blueprint, render_template, request, current_app
import requests

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        k = int(request.form.get('k', 5))
        summarizer = request.form.get('summarizer', 'facebook/bart-large-cnn')

        API_URL = current_app.config['API_URL']

        response = requests.post(f"{API_URL}/search", json={
            'query': query,
            'k': k,
            'summarizer': summarizer if summarizer != 'openai' else None
        })
        data = response.json()

        # Pass 'enumerate' to the template context
        return render_template(
            'results.html',
            query=query,
            documents=data['documents'],
            summary=data['summary'],
            enumerate=enumerate
        )

    return render_template('index.html')