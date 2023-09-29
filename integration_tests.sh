#!/bin/bash

# Set the API_URL environment variable to the local API server
export API_URL=http://localhost:8000

# Change to the maintainability directory
cd maintainability/

# Start the API server in the background
uvicorn api.src.main:app --port 8000 &
API_PID=$!
sleep 5

# Run the integration tests
pytest

# Kill the API server
kill -9 $API_PID
