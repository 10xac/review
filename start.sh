#!/bin/bash

# Default environment variables
# export RUN_STAGE=${RUN_STAGE:-"prod"}
export PORT=${PORT:-8000}
export HOST=${HOST:-"0.0.0.0"}
export WORKERS=${WORKERS:-4}

# Install requirements
pip install -r requirements.txt

# Run mode selection
if [ "$RUN_STAGE" = "dev" ]; then
    echo "Starting API in development mode..."
    uvicorn api.main:app --reload --host $HOST --port $PORT
else
    echo "Starting API in production mode..."
    uvicorn api.main:app --host $HOST --port $PORT --workers $WORKERS
fi