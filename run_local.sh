#!/bin/bash

echo "============================================================"
echo "        STARTING RAG SYSTEM LOCALLY"
echo "============================================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

echo "✓ Virtual environment found"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Load API key from .env
export $(cat .env | xargs)
echo "✓ API key loaded"
echo ""

# Kill any existing servers
echo "Stopping existing servers..."
lsof -ti:8000,3000 | xargs kill -9 2>/dev/null
sleep 2
echo "✓ Ports cleared"
echo ""

# Start backend
echo "Starting backend on port 8000..."
source venv/bin/activate
nohup python app/main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 5

# Test backend
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✓ Backend is responding"
else
    echo "❌ Backend failed to start"
    echo "Check backend.log for errors"
    exit 1
fi
echo ""

# Start frontend
echo "Starting frontend on port 3000..."
cd frontend
nohup python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo ""

# Wait for frontend
sleep 2

echo "============================================================"
echo "        ✓ SERVICES STARTED SUCCESSFULLY!"
echo "============================================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  or: lsof -ti:8000,3000 | xargs kill"
echo ""
echo "Opening browser..."
sleep 2
open http://localhost:3000 2>/dev/null || echo "Please open: http://localhost:3000"
