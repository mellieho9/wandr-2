#!/bin/bash
# Development script to run both Flask backend and React frontend

echo "🚀 Starting Social Video Processor Development Environment"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   Run: source .venv/bin/activate"
    echo ""
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
    echo ""
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $FLASK_PID $VITE_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Flask backend
echo "🐍 Starting Flask backend on http://localhost:8080..."
flask run --host=0.0.0.0 --port=8080 &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start Vite dev server
echo "⚛️  Starting React frontend on http://localhost:3000..."
cd frontend && npm run dev &
VITE_PID=$!
cd ..

echo ""
echo "✅ Development servers started!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8080"
echo "   Health:   http://localhost:8080/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $FLASK_PID $VITE_PID
