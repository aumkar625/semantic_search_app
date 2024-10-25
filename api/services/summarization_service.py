import os
import time
import logging
import google.generativeai as genai
from requests.exceptions import RequestException
from abstract.summarization_base import SummarizationBase

# Configure logging
logger = logging.getLogger(__name__)

# Configure the Generative AI model
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel(os.environ["GEMINI_MODEL_SUMMARY"])

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries


class SummarizationService(SummarizationBase):
    def summarize(self, docs, question):
        # Combine docs into a single text block, adding distinct separation
        text = '\n\n'.join(docs)[:3000]  # Adjust length as needed to fit context

        # Construct a prompt emphasizing a targeted, relevant summary
        prompt = (
            f"From the documents below, summarize the content that best answers the question. "
            f"Focus only on relevant information and avoid adding anything extra.\n\n"
            f"Question: {question}\n"
            f"Documents:\n{text}\n\n"
            f"Provide the best summary answer based solely on the provided documents."
        )

        # Retry loop for generating content
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Attempting summarization (Attempt {attempt})")
                response = model.generate_content(prompt)
                logger.info("Summary generated successfully.")
                return response.text  # Return if successful
            except RequestException as e:
                logger.error(f"Attempt {attempt} failed with error: {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("Max retries exceeded. Summarization failed.")
                    return None  # Return None or raise a custom exception based on needs
            except Exception as e:
                logger.error(f"Unexpected error during summarization: {e}")
                return None