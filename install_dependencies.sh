#!/bin/bash

# Exit on error
set -e

echo "Installing TenX Content Extractor dependencies..."

# Install Python dependencies
pip install -r app/requirements.txt

echo "Dependencies installed successfully!"
echo ""
echo "To run the application:"
echo "uvicorn app.main:app --host 0.0.0.0 --port 5061 --reload"
echo ""
echo "Note: Some features may require additional system dependencies:"
echo "- Git: For code analysis features"
echo "- Poppler: For advanced PDF processing"
echo ""
echo "On Ubuntu/Debian, you can install these with:"
echo "sudo apt-get update && sudo apt-get install -y git poppler-utils"
echo ""
echo "On macOS, you can install these with:"
echo "brew install git poppler" 