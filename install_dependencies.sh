#!/bin/bash

# Exit on error
set -e

echo "Installing TenX Content Extractor dependencies..."

# Install Python dependencies
pip install -r app/requirements.txt

echo "Dependencies installed successfully!"
echo ""
echo "To run the application:"
echo "uvicorn api.main:app --reload --host 0.0.0.0 --port 8008"
echo ""
echo "Note: Some features may require additional system dependencies:"
echo ""
