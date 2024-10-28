# data/load_data.py
from datasets import load_dataset

def load_documents():
    dataset = load_dataset('squad', split='train')
    documents = []

    for item in dataset:
        context = item['context']
        question = item['question']
        answer = item['answers']['text'][0]  # Taking the first answer

        # Combine the context, question, and answer into a single document
        document = f"Context: {context}\nQuestion: {question}\nAnswer: {answer}"
        documents.append(document)

    return documents