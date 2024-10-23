# Semantic Search Application

Welcome to the **Semantic Search Application**! This project leverages FastAPI, React, and Qdrant to provide a robust semantic search experience. Users can input queries, retrieve relevant documents from a vector database, and optionally generate summaries of the search results.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Docker Compose Services](#docker-compose-services)
- [API Endpoints](#api-endpoints)
  - [Search Endpoint](#search-endpoint)
- [Using `curl`](#using-curl)
  - [A. Search Without Summarization](#a-search-without-summarization)
  - [B. Search With Summarization](#b-search-with-summarization)
- [Docker Compose Debugging](#docker-compose-debugging)
  - [Viewing Logs](#viewing-logs)
  - [Accessing Containers](#accessing-containers)
  - [Rebuilding Containers](#rebuilding-containers)
- [Notes](#notes)

---

## Prerequisites

Before setting up the Semantic Search Application, ensure you have the following installed on your system:

- **Docker**: [Download and Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Download and Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git**: [Download and Install Git](https://git-scm.com/downloads)

> **Note:** Docker Desktop includes both Docker Engine and Docker Compose, so if you install Docker Desktop, you might already have Docker Compose installed.

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/semantic-search-app.git
   cd semantic-search-app
   touch .env
   GEMINI_API_KEY=your_gemini_api_key_here

Environment Variables
The application uses environment variables to manage configurations securely. Here's a breakdown of the necessary environment variables:

QDRANT_URL: The URL where the Qdrant vector database is accessible.
Default: http://qdrant:6333
GEMINI_API_KEY: (Required) Your Gemini API key for accessing Gemini services.
TRANSFORMERS_CACHE: Path to cache directory for Hugging Face transformers models.
Default: /app/cache/huggingface/transformers
REACT_APP_API_URL: URL for the API endpoint used by the React frontend.
Default: /api
Security Tip: Ensure that the .env file is excluded from version control to protect sensitive information. Add .env to your .gitignore file.


Docker Compose Services
The application is containerized using Docker Compose, orchestrating three primary services:

API Service (api)

Description: FastAPI backend handling search requests and interactions with Qdrant.
Image Build Context: ./api
Dockerfile: Dockerfile.api
Container Name: semantic_search_app_api_container
Ports: 8000:8000
Environment Variables:
QDRANT_URL: http://qdrant:6333
GEMINI_API_KEY: ${GEMINI_API_KEY}
TRANSFORMERS_CACHE: /app/cache/huggingface/transformers
Volumes:
qdrant_storage:/qdrant/storage
transformers_cache:/app/cache/huggingface/transformers
Dependencies: qdrant
Network: semantic_search_network
UI Service (app)

Description: React frontend providing the user interface for search interactions.
Image Build Context: ./semantic-search-ui
Dockerfile: Dockerfile
Container Name: semantic_search_ui_container
Ports: 80:80
Environment Variables:
REACT_APP_API_URL: /api
Dependencies: api
Network: semantic_search_network
Qdrant Service (qdrant)

Description: Qdrant vector database storing embeddings for semantic search.
Image: qdrant/qdrant
Container Name: qdrant
Ports: 6333:6333
Volumes:
qdrant_storage:/qdrant/storage
Network: semantic_search_network

Networks and Volumes
Network: semantic_search_network

Driver: bridge
Purpose: Facilitates communication between services using service names.
Volumes:

qdrant_storage: Persists Qdrant data.
transformers_cache: Caches Hugging Face transformers models to speed up loading times.

API Endpoints
The FastAPI backend exposes the following endpoints for semantic search functionalities:

Search Endpoint
URL: /api/search

Method: POST

Description: Processes a search query, retrieves relevant documents from Qdrant, and optionally generates a summary.

Request Body:

json
Copy code
{
  "query": "string",
  "k": integer (optional, default: 5),
  "summarizer": "string" (optional)
}
query: The search query string.
k: (Optional) Number of top results to retrieve. Defaults to 5.
summarizer: (Optional) Specifies the summarization model or API to use for generating a summary of the results.
Response:

json
Copy code
{
  "documents": ["string", ...],
  "summary": "string" (nullable)
}
documents: List of retrieved documents matching the query.
summary: Summary of the retrieved documents if the summarizer option was used; otherwise, null.

Using curl
You can interact with the API using curl commands from your terminal.

A. Search Without Summarization
Perform a search without generating a summary by omitting the summarizer field.

bash
Copy code
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "What is the capital of France?",
           "k": 2
         }'
Expected Response:

json
Copy code
{
  "documents": [
    "Paris is the capital of France.",
    "France's capital city is Paris."
  ],
  "summary": null
}
B. Search With Summarization
Perform a search and generate a summary by including the summarizer field.

bash
Copy code
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "What is the capital of France?",
           "k": 2,
           "summarizer": "default_summarizer"
         }'
Replace "default_summarizer" with your desired summarization option.

Expected Response:

json
Copy code
{
  "documents": [
    "Paris is the capital of France.",
    "France's capital city is Paris."
  ],
  "summary": "Paris is the capital of France."
}
Docker Compose Debugging
Ensure that all services are running correctly and troubleshoot any issues with the following commands.

Viewing Logs
Monitor logs for a specific service to identify issues.

API Service Logs:

bash
Copy code
docker-compose logs -f api
UI Service Logs:

bash
Copy code
docker-compose logs -f app
Qdrant Service Logs:

bash
Copy code
docker-compose logs -f qdrant
Accessing Containers
Access the shell of a running container for deeper inspection.

API Container:

bash
Copy code
docker exec -it semantic_search_app_api_container /bin/sh
UI Container:

bash
Copy code
docker exec -it semantic_search_ui_container /bin/sh
Qdrant Container:

bash
Copy code
docker exec -it qdrant /bin/sh
Rebuilding Containers
Rebuild and restart containers to apply changes.

bash
Copy code
docker-compose down
docker-compose up --build -d
Tip: Use the --no-deps flag with docker-compose up if you only want to rebuild a specific service without affecting others.

