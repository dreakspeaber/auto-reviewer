#!/bin/bash

# Function to kill processes on ports 3000 and 8000
kill_existing_processes() {
    echo "Killing existing processes on ports 3000 and 8000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
}

# Kill existing processes
kill_existing_processes

# Start backend
echo "Starting backend server..."
cd back
source ../venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend server..."
cd ../front
npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Development servers started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
