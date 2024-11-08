# services/summarization_service.py

import os
import logging
import asyncio
from typing import List
from requests.exceptions import RequestException

from abstract.summarization_base import SummarizationBase
import services.logger_base  # Ensure logging is configured

logger = logging.getLogger(__name__)

import google.generativeai as genai

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries


class SummarizationService(SummarizationBase):
    """Service for summarizing text using Gemini LLM."""

    def __init__(self):
        # Configure the Generative AI model
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_SUMMARY")

        if not api_key:
            logger.error("Gemini API key is not set. Please set GEMINI_API_KEY environment variable.")
            raise ValueError("Gemini API key is not set.")

        if not model_name:
            logger.error("Gemini model name is not set. Please set GEMINI_MODEL_SUMMARY environment variable.")
            raise ValueError("Gemini model name is not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"SummarizationService initialized with Gemini model: {model_name}")

    async def summarize(self, texts: List[str], question: str) -> str:
        """Summarizes the given texts using Gemini LLM."""
        try:
            # Combine texts into a single text block, adding distinct separation
            text = '\n\n'.join(texts)[:3000]  # Adjust length as needed to fit context
            logger.debug(f"Input text for summarization: {text}")
            logger.debug(f"The question is: {question}")

            # Construct a prompt emphasizing a targeted, relevant summary
            prompt = (
                f"From the documents below, summarize the content that best answers the question shared with tag question: from content with tag as Documents: "
                f"Focus only on relevant information and avoid adding anything extra and the.\n\n"
                f"Question: {question}\n"
                f"Documents:\n{text}\n\n"
                f"Provide the best summary answer based solely on the provided documents."
            )

            # Retry loop for generating content
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    logger.info(f"Attempting summarization (Attempt {attempt})")
                    # Since model.generate_content is blocking, run it in a thread
                    response = await asyncio.to_thread(self.model.generate_content, prompt)
                    summary = response.text  # Extract summary text from the response
                    logger.info("Summary generated successfully.")
                    return summary  # Return if successful
                except RequestException as e:
                    logger.error(f"Attempt {attempt} failed with request error: {e}", exc_info=True)
                    if attempt < MAX_RETRIES:
                        logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        logger.error("Max retries exceeded. Summarization failed.", exc_info=True)
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error during summarization: {e}", exc_info=True)
                    raise
        except Exception as e:
            logger.error(f"Error during summarization process: {e}", exc_info=True)
            raise