# services/schema.py

from typing import List, Optional
from pydantic import BaseModel, validator
from abstract.schema_base import SchemaBase


class Payload(BaseModel):
    """Encapsulates text and file_path for documents."""
    text: str
    file_path: Optional[str] = None


class SearchRequest(BaseModel, SchemaBase):
    query: str
    k: int = 5
    summarizer: Optional[bool] = False  # Changed to boolean flag

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Query must not be empty.')
        return v

    @validator('k')
    def k_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('The value of "k" must be positive.')
        return v


class Document(BaseModel, SchemaBase):
    payload: Payload
    score: float

    @validator('score')
    def score_must_be_between_zero_and_one(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Score must be between 0 and 1.')
        return v


class SearchResponse(BaseModel, SchemaBase):
    documents: List[Document]
    summary: Optional[str] = None
