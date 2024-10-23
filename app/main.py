# app/main.py
from flask import render_template, request
from app import app
import requests

API_URL = app.config['API_URL']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        k = int(request.form.get('k', 5))
        summarizer = request.form.get('summarizer', 'facebook/bart-large-cnn')

        response = requests.post(f'{API_URL}/search', json={
            'query': query,
            'k': k,
            'summarizer': summarizer if summarizer != 'openai' else None
        })
        data = response.json()
        return render_template('results.html', query=query, documents=data['documents'], summary=data['summary'])

    return render_template('index.html')
