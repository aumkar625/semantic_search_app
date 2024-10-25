from abstract.format_service_base import FormatServiceBase
from schemas import Document, Payload

class DocumentFormatter(FormatServiceBase):
    def format_documents(self, search_results):
        """Format search results into Document objects with text, file_path, and score."""
        formatted_documents = []
        for hit in search_results:
            payload = Payload(text=hit.payload.get("text", ""), file_path=hit.payload.get("file_path"))
            document = Document(
                text=payload.text,
                file_path=payload.file_path,
                score=hit.score
            )
            formatted_documents.append(document)
        return formatted_documents
