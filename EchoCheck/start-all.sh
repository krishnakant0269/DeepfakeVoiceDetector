# #!/bin/bash

# # EchoCheck Quick Start Script
# # This script starts all services for local development

# set -e  # Exit on error

# echo "🚀 Starting EchoCheck..."

# # Check if Docker is installed
# if command -v docker-compose &> /dev/null; then
#     echo "✅ Docker Compose found"
#     echo "🐳 Starting with Docker..."
#     docker-compose up --build
# else
#     echo "⚠️  Docker not found. Starting manually..."
    
#     # Check MongoDB
#     if ! pgrep -x "mongod" > /dev/null; then
#         echo "Starting MongoDB..."
#         mongod --fork --logpath /tmp/mongodb.log --dbpath ./data/db
#     fi
    
#     # Start AI Service
#     echo "🐍 Starting Python AI Service..."
#     cd ai_service
#     source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
#     pip install -q -r requirements.txt
#     python main.py &
#     AI_PID=$!
#     cd ..
    
#     # Start Backend
#     echo "🟢 Starting Node.js Backend..."
#     cd server
#     npm install --silent
#     npm run dev &
#     BACKEND_PID=$!
#     cd ..
    
#     # Start Frontend
#     echo "⚛️  Starting React Frontend..."
#     cd client
#     npm install --silent
#     npm start &
#     FRONTEND_PID=$!
#     cd ..
    
#     echo ""
#     echo "✅ All services started!"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo "📱 Frontend:    http://localhost:3000"
#     echo "🔧 Backend:     http://localhost:5000"
#     echo "🤖 AI Service:  http://localhost:8000"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     echo "Press Ctrl+C to stop all services"
    
#     # Cleanup on exit
#     trap "echo ''; echo 'Stopping services...'; kill $AI_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null; mongod --shutdown; echo 'Done!'" EXIT
    
#     # Wait
#     wait
# fi

#!/bin/bash

echo "🚀 Starting EchoCheck (Windows Mode)..."

# AI Service
echo "Starting AI Service..."
cd ai_service
python main.py &
AI_PID=$!
cd ..

# Backend
echo "Starting Backend..."
cd server
npm start &
BACKEND_PID=$!
cd ..

# Frontend
echo "Starting Frontend..."
cd client
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5000"
echo "AI Service: http://localhost:8000"

wait
