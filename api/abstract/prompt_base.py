# abstract/prompt_base.py

class PromptBase:
    """Interface for prompt services."""

    def get_prompt(self, **kwargs) -> str:
        """Returns the prompt with substituted variables."""
        raise NotImplementedError("Prompt service must implement `get_prompt` method.")