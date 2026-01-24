#!/bin/bash

# Run script for Synth application
# This script helps you run both backend and frontend

echo "=== Synth Application Runner ==="
echo ""
echo "Choose an option:"
echo "1. Run Backend only (FastAPI on port 8000)"
echo "2. Run Frontend only (Vite on port 5173)"
echo "3. Run Both (Backend + Frontend in separate terminals)"
echo "4. Install dependencies"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
  1)
    echo "Starting Backend..."
    cd backend || exit
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ;;
  2)
    echo "Starting Frontend..."
    cd frontend || exit
    npm run dev
    ;;
  3)
    echo "Starting Backend in background..."
    cd backend || exit
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    echo ""
    echo "Starting Frontend..."
    cd ../frontend || exit
    npm run dev
    # Kill backend when frontend exits
    kill $BACKEND_PID 2>/dev/null
    ;;
  4)
    echo "Installing Backend dependencies..."
    pip install -r requirements.txt
    echo ""
    echo "Installing Frontend dependencies..."
    cd frontend || exit
    npm install
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac
