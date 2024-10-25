from abstract.format_service_base import FormatServiceBase
from services.schema import Document, Payload

class DocumentFormatter(FormatServiceBase):
    def format_documents(self, search_results):
        """Format search results into Document objects with embedded payload and score."""
        formatted_documents = []
        for hit in search_results:
            # Create a Payload instance
            payload = Payload(
                text=hit.payload.get("text", ""),
                file_path=hit.payload.get("file_path")
            )
            # Create a Document instance, embedding the Payload instance
            document = Document(
                payload=payload,
                score=hit.score
            )
            formatted_documents.append(document)
        return formatted_documents
