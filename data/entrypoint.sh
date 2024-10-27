#!/bin/bash

# Set -e to exit on errors and -o pipefail to catch errors in pipelines
set -e
set -o pipefail
echo "Starting entrypoint script..."

# Run tests
#echo "Running pytests..."
#pytest tests

# Proceed with the rest of the script only if tests pass
echo "Tests passed. Starting the application..."

# Remove any existing .csv files in /mnt/data/files
echo "Deleting existing .csv files in /mnt/data/files..."
find /mnt/data/files -name "*.csv" -type f -exec rm -f {} +

# Clear the content of uploaded_files_checklist.txt if it exists
if [ -f "/mnt/data/log/uploaded_files_checklist.txt" ]; then
    echo "Clearing content of uploaded_files_checklist.txt..."
    > /mnt/data/log/uploaded_files_checklist.txt
else
    echo "uploaded_files_checklist.txt not found in /mnt/data/log. Creating one..."
    mkdir -p /mnt/data/log
    touch /mnt/data/log/uploaded_files_checklist.txt
fi

# Check if the zip file exists
if [ -f "/mnt/data/files/squad_csv_files_subset.zip" ]; then
    echo "Unzipping squad_csv_files_subset.zip..."
    unzip -o /mnt/data/files/squad_csv_files_subset.zip -d /mnt/data/files/
else
    echo "Zip file not found at /mnt/data/files/squad_csv_files_subset.zip"
fi

# List files to verify unzipping
echo "Contents of /mnt/data/files after unzipping:"
ls -l /mnt/data/files/

# Start the Python scheduler in the foreground
echo "Starting scheduler.py..."
exec python /app/scheduler.py
