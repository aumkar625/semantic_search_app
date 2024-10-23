# summarization_module/summarization.py

from transformers import pipeline
import os

# Initialize a dictionary to store summarizer pipelines
summarizer_pipelines = {}

# Default summarization model
DEFAULT_SUMMARIZER_MODEL = 'facebook/bart-large-cnn'

# Load the default summarizer pipeline when the module is imported
summarizer_pipelines[DEFAULT_SUMMARIZER_MODEL] = pipeline('summarization', model=DEFAULT_SUMMARIZER_MODEL)

def summarize(docs, summarizer_choice=None):
    text = ' '.join(docs)[:1000]  # Limit text length for summarization

    if summarizer_choice == 'openai':
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following text:\n{text}",
            max_tokens=150
        )
        summary = response.choices[0].text.strip()
    else:
        # Determine the model to use
        model_name = summarizer_choice or DEFAULT_SUMMARIZER_MODEL

        # Check if the pipeline is already loaded
        if model_name not in summarizer_pipelines:
            # Load and cache the summarizer pipeline for the new model
            summarizer_pipelines[model_name] = pipeline('summarization', model=model_name)

        # Use the cached pipeline
        summarizer = summarizer_pipelines[model_name]
        summary = summarizer(text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']

    return summary