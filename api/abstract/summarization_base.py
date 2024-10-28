from typing import List

class SummarizationBase:
    """Interface for summarization services."""
    
    def summarize(self, docs: List[str], summarizer_choice: str) -> str:
        raise NotImplementedError("Summarization service must implement `summarize` method.")

