class FormatServiceBase:
    """Interface for formatting services."""

    def format_documents(self, search_results):
        raise NotImplementedError("Format service must implement `format_documents` method.")