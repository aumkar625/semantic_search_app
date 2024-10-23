# summarization_module/summarization.py
from transformers import pipeline
import os

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
        # Default to local Hugging Face model
        summarizer = pipeline('summarization', model=summarizer_choice or 'facebook/bart-large-cnn')
        summary = summarizer(text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']

    return summary
