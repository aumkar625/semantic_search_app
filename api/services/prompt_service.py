# services/prompt_service.py

import os
import logging
from string import Template

from abstract.prompt_base import PromptBase

logger = logging.getLogger(__name__)

class FilePromptService(PromptBase):
    """Service for loading and providing prompt templates from a file."""

    def __init__(self, prompt_template_file=None):
        if not prompt_template_file:
            prompt_template_file = os.getenv('PROMPT_TEMPLATE_FILE', 'prompt_template.txt')
        self.prompt_template_file = prompt_template_file
        try:
            with open(self.prompt_template_file, 'r') as f:
                template_content = f.read()
            self.prompt_template = Template(template_content)
            logger.info(f"Loaded prompt template from {self.prompt_template_file}")
        except Exception as e:
            logger.error(f"Error reading prompt template file '{self.prompt_template_file}': {e}")
            raise

    def get_prompt(self, **kwargs) -> str:
        """Returns the prompt with variables substituted."""
        try:
            prompt = self.prompt_template.safe_substitute(**kwargs)
            return prompt
        except Exception as e:
            logger.error(f"Error substituting variables in prompt template: {e}")
            raise