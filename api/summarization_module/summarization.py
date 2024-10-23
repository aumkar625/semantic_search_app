# summarization_module/summarization.py
import os
import google.generativeai as genai


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-1.5-flash')

def summarize(docs, summarizer_choice=None):
    text = ' '.join(docs)[:1000]  # Limit text length for summarization
    prompt = f"Summarize the following text:\n{text}"
    response = model.generate_content(prompt)
    return response