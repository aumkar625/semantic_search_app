# data/scheduler.py
import time
import schedule
import logging
import os
from file_uploader_to_qdrant import FileUploaderToQdrant

# Load environment variables for directory and URL
qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
mounted_dir = "/mnt/data/"  # Ensure this path is where your CSV files are mounted
log_dir = os.path.join(mounted_dir, "log")
os.makedirs(log_dir, exist_ok=True)

# Set up logging to 'service.log' in the log directory
log_file_path = os.path.join(log_dir, "service.log")
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
RUN_INTERVAL = 10  # Run interval in seconds
MAX_RETRIES = 3  # Number of retries
RETRY_DELAY = 5  # Delay between retries in seconds

# Initialize the FileUploaderToQdrant
uploader = FileUploaderToQdrant(qdrant_url=qdrant_url, mounted_dir=mounted_dir)

def scheduled_job():
    """Function that runs the job with retry logic."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Starting scheduled job: Syncing files with Qdrant.")
            uploader.sync_files_with_qdrant()
            logger.info("Scheduled job completed successfully.")
            break
        except Exception as e:
            logger.error(f"Job failed on attempt {attempt}/{MAX_RETRIES}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Max retries exceeded. Job failed.")

# Schedule the job
schedule.every(RUN_INTERVAL).seconds.do(scheduled_job)

# Run the scheduled job indefinitely
if __name__ == "__main__":
    logger.info("Starting scheduler for Qdrant file uploader.")
    while True:
        schedule.run_pending()
        time.sleep(1)
