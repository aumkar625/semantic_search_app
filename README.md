# Semantic Search Engine

A semantic search engine that takes a user's question and returns the top matching answers based on the [Stanford Question Answering Dataset (SQuAD)](https://www.kaggle.com/datasets/stanfordu/stanford-question-answering-dataset). The engine also provides summaries of the documents relevant to the question asked.

![img_1.png](img_1.png)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Environment Setup](#environment-setup)
- [Services Overview](#services-overview)
- [Running the Application](#running-the-application)
- [API Usage](#api-usage)
- [Configuration](#configuration)
- [Data and Logs Mounting](#data-and-logs-mounting)

## Features

- **Semantic Search**: Retrieve top K documents matching the user's question semantically.
- **Summarization**: Optionally generate a summary of the relevant documents.
- **Interactive UI**: A React-based user interface for inputting questions and viewing results.
- **Data Synchronization**: Automated data uploader that syncs CSV files with the vector database.
- **Testing**: Comprehensive unit and integration tests for API validation.

## Architecture

The project consists of multiple Dockerized services orchestrated using Docker Compose:

- **API Service**: A FastAPI application handling search and summarization requests.
- **UI Service**: A React-based frontend for user interaction.
- **Vector Database**: Qdrant service for storing and querying vector embeddings.
- **Data Uploader**: A Python scheduler for syncing CSV files with the vector database.
- **Testing Service**: Runs unit and integration tests using pytest.

## Environment Setup

1. **Install Docker**: Follow the [official Docker installation guide](https://docs.docker.com/engine/install/) for your operating system.

   - If your machine is behind a firewall or VPN, ensure that you configure proxy settings accordingly.

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/aumkar625/semantic_search_app.git
   cd your_repository
   git chekout main
   cp .env.template .env
   GEMINI_API_KEY=your_gemini_api_key
   DEBUG=True  # Set to False in production
   
## Services Overview
1. **Qdrant (Vector Database)**
    Description: A vector database service that stores embeddings for the dataset. Running on a single node for simplicity.
    Technology: Qdrant
2. **API Service**
     Description: A FastAPI application that receives user queries, generates embeddings, searches Qdrant for top K documents, and optionally summarizes the results using a language model.

   Endpoints:

   Search Endpoint:
   POST /api/search
   Request:
       {
           "query": "Your question here",
           "k": 2,
           "summarizer": "true"  # Optional
       }

   Response:
       {
           "documents": [
           {
               "payload": {
                   "text": "Document text here",
                   "file_path": "/path/to/file.csv"
                           },
               "score": 0.51070035
           },
           {
               "payload": {
                   "text": "Another document text",
                   "file_path": "/path/to/another_file.csv"
                           },
               "score": 0.34983337
        }
                           ],
   "summary": "Summary text here."  # Present if summarizer is true
       }

3. **UI Service**
   Description: A React-based user interface where users can input questions, specify the number of top documents to return, and choose between list view and summary view.

    Access: http://localhost/


4. **Data Uploader**
   Description: A Python-based scheduler that monitors the data/files directory and uploads new CSV files to Qdrant. If a file is deleted from the directory, its corresponding embeddings are removed from Qdrant.

    Data:
    By default, a subset of files from the data/files folder is loaded.
    To load the entire dataset (~86k records), unzip the squad_csv_files.zip file:
    cd data/files
    unzip squad_csv_files.zip

    The uploader will automatically start loading the files.

    **Logs:**
    - The uploader logs are available at data/log/service.log, which is mounted to the local machine.

5. **Testing Service**
   Description: Runs all unit and integration tests for the API using pytest.

## Running the Application
1. **Build All Services:**
    - docker compose build
2. **Start All Services:**
    - docker compose up api
    - To run services in the background:
    - docker compose up -d
    - You might encounter test failures related to cache permissions when running the tests service. If you prefer to ignore test results for now.
    - 
3. **Data Loading:**
    - The uploader service will automatically start uploading data to Qdrant.
    - Monitor the upload status by checking data/log/service.log, which is mounted to the local machine.
    - check logs for data upload
        - using docker compose:
            docker compose logs uploader -f
        - detailed log at: 
            data/log/service.log (mounted on to data folder in local machine on repo folder data)
    - Once you see that at least one batch has succeeded in the logs, the data and collection are available in Qdrant, and you can proceed to the next step

4. **Access the UI:**
    - Open http://localhost/ in your web browser.

## API Usage
**Search Endpoint**
   - URL: http://localhost:8000/api/search

Method: POST

{
  "query": "Your question here",
  "k": 2,
  "summarizer": "true"  # Optional
}

Example:

curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "What is the capital of France?",
           "k": 2
         }'

Sample Response:
{
  "documents": [
    {
      "payload": {
        "text": "Context: Paris is the capital and most populous city of France...",
        "file_path": "/mnt/data/files/squad_part_4.csv"
      },
      "score": 0.51070035
    },
    {
      "payload": {
        "text": "Context: France, officially the French Republic...",
        "file_path": "/mnt/data/files/squad_part_5.csv"
      },
      "score": 0.34983337
    }
  ],
  "summary": "Paris is the capital of France."
}
## Configuration
***Environment Variables (.env)***

    QDRANT_URL=http://qdrant:6333
    GEMINI_API_KEY=your_gemini_api_key
    GEMINI_MODEL_SUMMARY=gemini-1.5-flash
    SENTENCE_TRANSFORMER=all-MiniLM-L6-v2
    TRANSFORMERS_CACHE=/app/cache/huggingface/transformers
    TABLE=squad_dataset
    REACT_APP_API_URL=/api
    DEBUG=True
    PROMPT_TEMPLATE_FILE=/path/to/your/prompt_template.txt
    QDRANT_URL: URL of the Qdrant service.
    GEMINI_API_KEY: API key for the language model service.
    GEMINI_MODEL_SUMMARY: Model name for summarization (e.g., gemini-1.5-flash).
    SENTENCE_TRANSFORMER: Name of the sentence transformer model (e.g., all-MiniLM-L6-v2).
    TRANSFORMERS_CACHE: Path to cache HuggingFace transformers.
    TABLE: Name of the collection in Qdrant (e.g., squad_dataset).
    REACT_APP_API_URL: API URL for the UI.
    DEBUG: Set to True for verbose logging.
    PROMPT_TEMPLATE_FILE: Path to the prompt template file (if applicable).

## Data and Logs Mounting
***Data Files:***
   - The data/files directory is mounted to the local machine.
   - You can place your CSV files in this directory, and the uploader will process them.

***Logs:***
   - The uploader logs are stored in data/log/service.log, which is mounted to the local machine.
   - You can monitor the uploader's status by checking this log file.




