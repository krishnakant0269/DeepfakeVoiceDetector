#!/bin/bash

# EchoCheck Setup Script
# Run this to set up your development environment

echo "🚀 EchoCheck Setup Starting..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create project structure
echo -e "${YELLOW}📁 Creating project structure...${NC}"
mkdir -p EchoCheck/{client,server,ai_service}
mkdir -p EchoCheck/server/{controllers,models,routes,middleware,config}
mkdir -p EchoCheck/ai_service/{models,utils}
mkdir -p EchoCheck/server/uploads

# Initialize Node.js projects
echo -e "${YELLOW}📦 Initializing Node.js projects...${NC}"
cd EchoCheck/server && npm init -y
cd ../client && npx create-react-app .
cd ../..

# Install server dependencies
echo -e "${YELLOW}📦 Installing server dependencies...${NC}"
cd EchoCheck/server
npm install express mongoose multer axios cors dotenv bcryptjs jsonwebtoken
npm install -D nodemon

# Create .env file
cat > .env << EOF
PORT=5000
MONGODB_URI=mongodb://localhost:27017/echocheck
AI_SERVICE_URL=http://localhost:8000
JWT_SECRET=$(openssl rand -hex 32)
EOF

# Setup Python environment
echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"
cd ../ai_service
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
transformers==4.35.2
torch==2.1.0
torchaudio==2.1.0
librosa==0.10.1
vosk==0.3.45
soundfile==0.12.1
numpy==1.24.3
scikit-learn==1.3.2
python-multipart==0.0.6
EOF

pip install -r requirements.txt

# Download Vosk model
echo -e "${YELLOW}⬇️ Downloading Vosk speech model (this may take a few minutes)...${NC}"
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip
cd ../..

# Create start scripts
echo -e "${YELLOW}📝 Creating start scripts...${NC}"
cat > start-dev.sh << 'EOF'
#!/bin/bash

# Start all services for development

echo "Starting EchoCheck services..."

# Start MongoDB (assumes MongoDB is installed)
mongod --fork --logpath /tmp/mongodb.log

# Start AI Service
cd ai_service
source venv/bin/activate
python main.py &
AI_PID=$!
cd ..

# Start Backend
cd server
npm run dev &
BACKEND_PID=$!
cd ..

# Start Frontend
cd client
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5000"
echo "AI Service: http://localhost:8000"

# Wait for Ctrl+C
trap "kill $AI_PID $BACKEND_PID $FRONTEND_PID; mongod --shutdown" EXIT
wait
EOF

chmod +x start-dev.sh

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the IMPLEMENTATION_GUIDE.md for detailed code"
echo "2. Make sure MongoDB is installed and running"
echo "3. Run ./start-dev.sh to start all services"
echo ""
echo "Access the app at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend: http://localhost:5000"
echo "  - AI Service: http://localhost:8000"
