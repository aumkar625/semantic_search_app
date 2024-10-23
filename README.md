# Semantic Search Application

This is a semantic search application that allows users to search for documents and receive a summary of the top results. It uses a **Flask** frontend, a **FastAPI** backend, and **Qdrant** as the vector database. The application is containerized using **Docker** and can be easily deployed locally or in a cloud environment.

---

## **Table of Contents**

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up Environment Variables](#2-set-up-environment-variables)
  - [3. Build and Run Docker Containers](#3-build-and-run-docker-containers)
  - [4. Generate Embeddings and Upload to Qdrant](#4-generate-embeddings-and-upload-to-qdrant)
  - [5. Access the Application](#5-access-the-application)
- [Testing](#testing)
- [Deployment to Cloud](#deployment-to-cloud)
- [Additional Notes](#additional-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## **Prerequisites**

- **Operating System:** macOS (or any system with Docker support)
- **Python:** Version 3.7 or higher
- **Docker and Docker Compose:** Ensure Docker is installed and running
- **OpenAI API Key:** (Optional) If you plan to use OpenAI for summarization

---


---

## **Setup Instructions**

### **1. Clone the Repository**

Clone the repository to your local machine:

```bash

git clone https://github.com/yourusername/semantic_search_app.git
cd semantic_search_app

# setup_project.py

import os

project_structure = {
    # [The project_structure dictionary as provided in the previous assistant's response]
    # For brevity, please copy the updated project_structure from the previous response here.
}

def create_project_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_project_structure(path, content)
        else:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

def main():
    base_path = os.getcwd()
    create_project_structure(base_path, project_structure)
    print("Project structure created successfully.")
    print("\nNext steps:")
    print("1. Navigate into the 'semantic_search_app' directory:")
    print("   cd semantic_search_app")
    print("2. Set up environment variables by creating a '.env' file with your OpenAI API key.")
    print("3. Build and run the Docker containers with 'docker-compose up --build'.")
    print("4. In another terminal, generate embeddings by running:")
    print("   docker exec -it api bash")
    print("   cd /app")
    print("   python embeddings/generate_embeddings.py")
    print("5. Access the application at 'http://localhost:5000'.")

if __name__ == "__main__":
    main()


python3 setup_project.py

cp .env.example .env

touch .env

OPENAI_API_KEY=your_openai_api_key

docker-compose up --build

# Access the 'api' service container
docker exec -it api bash

# Navigate to the application directory
cd /app

# Generate embeddings and upload to Qdrant
python embeddings/generate_embeddings.py


Access the Application
Flask UI: Open your web browser and navigate to http://localhost:5000.
API Documentation: Access the Swagger UI at http://localhost:8000/docs.

pip install pytest

pytest tests/

