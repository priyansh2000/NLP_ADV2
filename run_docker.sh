#!/bin/bash

echo "============================================================"
echo "        STARTING RAG SYSTEM WITH DOCKER COMPOSE"
echo "============================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your GOOGLE_API_KEY"
    exit 1
fi

echo "✓ .env file exists"
echo ""

# Stop any local servers
echo "Stopping local servers on ports 8000 and 3000..."
lsof -ti:8000,3000 | xargs kill -9 2>/dev/null
echo "✓ Ports cleared"
echo ""

# Build and start services
echo "Building and starting Docker services..."
echo "This may take 5-10 minutes on first run..."
echo ""

docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "        ✓ SERVICES STARTED SUCCESSFULLY!"
    echo "============================================================"
    echo ""
    echo "Backend API: http://localhost:8000"
    echo "Frontend UI: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    echo ""
    echo "Opening browser..."
    sleep 3
    open http://localhost:3000 2>/dev/null || echo "Please open: http://localhost:3000"
else
    echo ""
    echo "❌ Failed to start services"
    echo ""
    echo "Check logs: docker-compose logs"
    echo ""
    echo "If you have network issues, run locally instead:"
    echo "  ./run_local.sh"
fi
