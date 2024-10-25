from typing import List, Optional
from pydantic import BaseModel, validator
from abstract.schema_base import SchemaBase

class Payload(BaseModel):
    """Encapsulates text and file_path for documents."""
    text: Optional[str] = ""
    file_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert payload to dictionary format."""
        return self.dict()


class SearchRequest(BaseModel, SchemaBase):
    query: str
    k: int = 5
    summarizer: Optional[str] = None

    def validate(self):
        """Custom validation logic if needed."""
        if not self.query:
            raise ValueError("Query must not be empty.")
        if self.k <= 0:
            raise ValueError("The value of 'k' must be positive.")

    def to_dict(self) -> dict:
        return self.dict()


class Document(BaseModel, SchemaBase):
    payload: Payload  # Embed the payload within the document
    score: float

    def validate(self):
        """Custom validation logic for Document."""
        if not self.payload.text:
            raise ValueError("Document text must not be empty.")
        if self.score < 0 or self.score > 1:
            raise ValueError("Score must be between 0 and 1.")

    def to_dict(self) -> dict:
        """Convert document to dictionary format, including embedded payload."""
        data = self.dict()
        data['payload'] = self.payload.to_dict()  # Convert payload to dict within document
        return data


class SearchResponse(BaseModel, SchemaBase):
    documents: List[Document]
    summary: Optional[str] = None

    def validate(self):
        """Custom validation logic for SearchResponse."""
        if not self.documents:
            raise ValueError("SearchResponse must contain at least one document.")

    def to_dict(self) -> dict:
        return self.dict()