#!/bin/bash

# Exit on error
set -e

echo "Building application for production..."

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose down

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose build
docker-compose up -d

echo "Application is now running!"
echo "Backend API available at: https://user-management.10academy.org/"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop the application: docker-compose down" 
