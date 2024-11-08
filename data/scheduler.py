# scheduler.py

import time
import schedule
import logging
import os
from file_uploader_to_qdrant import FileUploaderToQdrant

# Load environment variables for directory and URL
qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
mounted_dir = "/mnt/data/"  # Ensure this path is where your CSV files are mounted
log_dir = os.path.join(mounted_dir, "log")
qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
os.makedirs(log_dir, exist_ok=True)

# Set up logging to 'service.log' in the log directory
log_file_path = os.path.join(log_dir, "service.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
RUN_INTERVAL = 10  # Run interval in seconds

# Initialize the FileUploaderToQdrant
uploader = FileUploaderToQdrant(qdrant_url=qdrant_url, mounted_dir=mounted_dir,qdrant_api_key=qdrant_api_key)

def scheduled_job():
    """Function that runs the job."""
    try:
        logger.info("Starting scheduled job: Syncing files with Qdrant.")
        uploader.sync_files_with_qdrant()
        logger.info("Scheduled job completed successfully.")
    except Exception as e:
        logger.exception(f"Job failed: {e}")

# Schedule the job
schedule.every(RUN_INTERVAL).seconds.do(scheduled_job)

# Run the scheduled job indefinitely
if __name__ == "__main__":
    logger.info("Starting scheduler for Qdrant file uploader.")
    while True:
        schedule.run_pending()
        time.sleep(1)
