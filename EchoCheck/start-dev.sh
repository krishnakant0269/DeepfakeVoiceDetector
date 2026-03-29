# #!/bin/bash

# # Start all services for development

# echo "Starting EchoCheck services..."

# # Start MongoDB (assumes MongoDB is installed)
# mongod --fork --logpath /tmp/mongodb.log

# # Start AI Service
# cd ai_service
# source venv/bin/activate
# python main.py &
# AI_PID=$!
# cd ..

# # Start Backend
# cd server
# npm run dev &
# BACKEND_PID=$!
# cd ..

# # Start Frontend
# cd client
# npm start &
# FRONTEND_PID=$!
# cd ..

# echo "✅ All services started!"
# echo "Frontend: http://localhost:3000"
# echo "Backend: http://localhost:5000"
# echo "AI Service: http://localhost:8000"

# # Wait for Ctrl+C
# trap "kill $AI_PID $BACKEND_PID $FRONTEND_PID; mongod --shutdown" EXIT
# wait
#!/bin/bash

echo "Starting EchoCheck services..."

# AI Service
cd EchoCheck/ai_service
python main.py &
AI_PID=$!
cd ../..

# Backend
cd EchoCheck/server
npm start &
BACKEND_PID=$!
cd ../..

# Frontend
cd EchoCheck/client
npm start &
FRONTEND_PID=$!
cd ../..

echo "✅ All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5000"
echo "AI Service: http://localhost:8000"

wait
