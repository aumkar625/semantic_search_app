#!/bin/bash

# Variables
API_URL="http://localhost:8000/api/search"
NUM_REQUESTS_PER_SECOND=${1:-5}    # Default to 5 requests per second if not specified
TEST_DURATION_SECONDS=${2:-10}     # Default to 10 seconds if not specified

# List of questions
QUESTIONS=(
    "What is the capital of India?"
    "Who is the president of the United States?"
    "What is the capital of France?"
    "Who is the prime minister of Canada?"
    "What is the capital of Germany?"
    "Who is the president of Brazil?"
    "What is the capital of Japan?"
    "Who is the president of China?"
    "What is the capital of Italy?"
    "Who is the prime minister of the United Kingdom?"
    "What is the capital of Australia?"
    "Who is the president of Mexico?"
    "What is the capital of South Africa?"
    "Who is the president of Russia?"
    "What is the capital of Egypt?"
    "Who is the prime minister of New Zealand?"
    "What is the capital of Spain?"
    "Who is the president of Argentina?"
    "What is the capital of Turkey?"
    "Who is the prime minister of Israel?"
    "What is the capital of Saudi Arabia?"
    "Who is the president of South Korea?"
    "What is the capital of Sweden?"
    "Who is the prime minister of Greece?"
    "What is the capital of Norway?"
    "Who is the president of Portugal?"
    "What is the capital of Denmark?"
    "Who is the prime minister of Finland?"
    "What is the capital of Netherlands?"
    "Who is the president of Poland?"
    "What is the capital of Belgium?"
    "Who is the prime minister of Austria?"
    "What is the capital of Switzerland?"
    "Who is the president of Ireland?"
    "What is the capital of Qatar?"
    "Who is the prime minister of Singapore?"
    "What is the capital of Malaysia?"
    "Who is the president of Philippines?"
    "What is the capital of Thailand?"
    "Who is the prime minister of Vietnam?"
    "What is the capital of Indonesia?"
    "Who is the president of Nigeria?"
    "What is the capital of Kenya?"
    "Who is the prime minister of Iceland?"
    "What is the capital of Hungary?"
    "Who is the president of Chile?"
    "What is the capital of Peru?"
    "Who is the prime minister of Lebanon?"
    "What is the capital of Czech Republic?"
    "Who is the president of Venezuela?"
)

# Function to get current time in milliseconds (compatible with macOS)
current_time_ms() {
    python -c 'import time; print(int(time.time() * 1000))'
}

# Initialize total counters
TOTAL_REQUEST_COUNT=0
TOTAL_TIME_MS=0

echo "Starting load test for $TEST_DURATION_SECONDS seconds with $NUM_REQUESTS_PER_SECOND requests per second..."

START_TIME=$(current_time_ms)

# Loop over each second of the test duration
for ((second = 1; second <= TEST_DURATION_SECONDS; second++)); do
    SECOND_REQUEST_COUNT=0
    SECOND_TOTAL_TIME_MS=0
    SECOND_START_TIME=$(current_time_ms)

    # Send the specified number of requests per second
    for ((i = 0; i < NUM_REQUESTS_PER_SECOND; i++)); do
        REQUEST_START_TIME=$(current_time_ms)

        # Select a random question
        QUERY="${QUESTIONS[RANDOM % ${#QUESTIONS[@]}]}"

        # Send the API request and measure the response time
        RESPONSE_TIME=$(curl -s -o /dev/null -w '%{time_total}' -X POST "$API_URL" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$QUERY\", \"k\": 30}")

        # Convert response time to milliseconds
        REQ_TIME_MS=$(awk "BEGIN {print $RESPONSE_TIME * 1000}")

        # Update counters
        TOTAL_TIME_MS=$(awk "BEGIN {print $TOTAL_TIME_MS + $REQ_TIME_MS}")
        SECOND_TOTAL_TIME_MS=$(awk "BEGIN {print $SECOND_TOTAL_TIME_MS + $REQ_TIME_MS}")
        TOTAL_REQUEST_COUNT=$((TOTAL_REQUEST_COUNT + 1))
        SECOND_REQUEST_COUNT=$((SECOND_REQUEST_COUNT + 1))

        REQUEST_END_TIME=$(current_time_ms)
        REQUEST_DURATION_MS=$((REQUEST_END_TIME - REQUEST_START_TIME))

        # Adjust sleep time to maintain requests per second
        SLEEP_TIME_SEC=$(awk "BEGIN {sleep_time = (1 / $NUM_REQUESTS_PER_SECOND) - ($REQUEST_DURATION_MS / 1000); if (sleep_time > 0) print sleep_time; else print 0}")
        sleep $SLEEP_TIME_SEC
    done

    # Calculate and print average response time for the current second
    if [[ $SECOND_REQUEST_COUNT -gt 0 ]]; then
        SECOND_AVERAGE_TIME_MS=$(awk "BEGIN {print $SECOND_TOTAL_TIME_MS / $SECOND_REQUEST_COUNT}")
        echo "Second $second: Average response time = $SECOND_AVERAGE_TIME_MS ms"
    else
        echo "Second $second: No requests sent."
    fi

    # Wait until the next second starts
    SECOND_END_TIME=$(current_time_ms)
    SECOND_ELAPSED_TIME_MS=$((SECOND_END_TIME - SECOND_START_TIME))
    if [[ $SECOND_ELAPSED_TIME_MS -lt 1000 ]]; then
        SLEEP_TIME_MS=$((1000 - SECOND_ELAPSED_TIME_MS))
        sleep $(awk "BEGIN {print $SLEEP_TIME_MS / 1000}")
    fi
done

END_TIME=$(current_time_ms)
TOTAL_DURATION_MS=$((END_TIME - START_TIME))
TOTAL_DURATION_SEC=$(awk "BEGIN {print $TOTAL_DURATION_MS / 1000}")

# Calculate overall average response time
if [[ $TOTAL_REQUEST_COUNT -gt 0 ]]; then
    AVERAGE_TIME_MS=$(awk "BEGIN {print $TOTAL_TIME_MS / $TOTAL_REQUEST_COUNT}")
else
    AVERAGE_TIME_MS="N/A"
fi

# Display final results
echo "Load test completed."
echo "Total requests fired: $TOTAL_REQUEST_COUNT"
echo "Total time taken: $TOTAL_DURATION_SEC seconds"
echo "Average time per request: $AVERAGE_TIME_MS milliseconds"