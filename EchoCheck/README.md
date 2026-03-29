# 🛡️ EchoCheck - AI-Powered Vishing Detection System

EchoCheck is a cutting-edge anti-vishing platform that uses artificial intelligence to detect phone scams through a **two-pillar defense system**:

1. **Pillar A: Deepfake Detection** - Uses Wav2Vec2 and spectral analysis to identify AI-generated voices
2. **Pillar B: Intent Analysis** - Uses BERT and pattern matching to detect scam scripts

## 🎯 Features

- **Real-time Audio Analysis**: Record or upload suspicious calls
- **Deepfake Voice Detection**: Identifies synthetic/AI-generated voices
- **Scam Script Detection**: Recognizes common vishing patterns
- **Risk Scoring**: Combines both analyses into actionable risk levels
- **Scan History**: Track and review all analyzed calls
- **User Authentication**: Secure JWT-based authentication
- **Privacy-First**: All processing happens on your server

## 🏗️ Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   Node.js   │────▶│   Python    │
│  Frontend   │     │   Backend   │     │ AI Service  │
│  (Port 3000)│     │  (Port 5000)│     │ (Port 8000) │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │   MongoDB   │
                    │ (Port 27017)│
                    └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Node.js 18+, Python 3.10+, MongoDB

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/echocheck.git
cd echocheck

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# AI Service: http://localhost:8000
```

### Option 2: Manual Setup
```bash
# 1. Start MongoDB
mongod

# 2. Setup Python AI Service
cd ai_service
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download Vosk model
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
cd ../..

# Run AI service
python main.py

# 3. Setup Node.js Backend (new terminal)
cd server
npm install
mkdir uploads
npm run dev

# 4. Setup React Frontend (new terminal)
cd client
npm install
npm start
```

## 📋 Environment Variables

### Backend (.env)
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/echocheck
AI_SERVICE_URL=http://localhost:8000
JWT_SECRET=your-secret-key-here
NODE_ENV=development
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
```

## 🧪 Testing the System

1. **Register/Login** at http://localhost:3000
2. **Record or Upload** a suspicious audio file
3. **Analyze** - The system will:
   - Detect if the voice is AI-generated (Pillar A)
   - Check for scam patterns in the transcript (Pillar B)
   - Provide a risk score: LOW, MEDIUM, HIGH, or CRITICAL
4. **View History** - See all your past scans

## 📊 How It Works

### Deepfake Detection (Pillar A)

Uses spectral analysis to detect:
- High-frequency artifacts
- Unnatural breathing patterns
- Phase inconsistencies
```python
# Deepfakes typically have lower high-frequency content
hf_ratio = high_freq_energy / total_energy
is_deepfake = hf_ratio < 0.15
```

### Scam Intent Detection (Pillar B)

1. **Speech-to-Text**: Vosk converts audio to text
2. **BERT Classification**: Zero-shot classification for scam detection
3. **Pattern Matching**: Regex patterns for known scam phrases
4. **Urgency Detection**: Identifies pressure tactics

### Risk Calculation
```python
combined_score = (deepfake_confidence * 0.6) + (scam_confidence * 0.4)

if score > 0.8: CRITICAL
if score > 0.6: HIGH
if score > 0.4: MEDIUM
else: LOW
```

## 🔧 Configuration

### Customizing Scam Patterns

Edit `ai_service/utils/scam_patterns.json`:
```json
{
  "financial_urgency": [
    "your account.*suspended",
    "unauthorized transaction"
  ],
  "custom_category": [
    "your custom pattern here"
  ]
}
```

### Using a Different AI Model

Replace Wav2Vec2 with your fine-tuned model:
```python
# In ai_service/models/deepfake_detector.py
self.model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "./your_custom_model"
)
```

## 📈 Model Training

### Fine-tuning Wav2Vec2 on Deepfake Data
```python
from transformers import Wav2Vec2ForSequenceClassification, Trainer

# Load pre-trained model
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "facebook/wav2vec2-base",
    num_labels=2  # real/fake
)

# Train on your dataset
# Recommended datasets:
# - ASVspoof 2021
# - WaveFake
# - In-The-Wild
```

## 🐳 Production Deployment

### Using Docker Compose (Production)
```yaml
# docker-compose.prod.yml
services:
  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
```

### Cloud Deployment

**AWS:**
```bash
# Deploy to ECS/Fargate
aws ecs create-cluster --cluster-name echocheck
# ... (see AWS deployment guide)
```

**GCP:**
```bash
# Deploy to Cloud Run
gcloud run deploy echocheck-ai --source ./ai_service
```

## 🔒 Security Considerations

- ✅ JWT authentication for all API endpoints
- ✅ Audio files deleted immediately after analysis
- ✅ Rate limiting on analysis endpoint
- ✅ Input validation and sanitization
- ✅ HTTPS recommended for production
- ✅ Environment variables for secrets

## 📊 API Endpoints

### Authentication
```
POST /api/user/register
POST /api/user/login
GET  /api/user/me
```

### Audio Analysis
```
POST /api/audio/analyze
GET  /api/audio/history
```

### AI Service
```
POST /analyze (multipart/form-data)
GET  /health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Wav2Vec2**: Facebook AI Research
- **BERT**: Google Research
- **Vosk**: Alpha Cephei
- **ASVspoof**: Anti-spoofing community

## 📧 Contact

For questions or support, please open an issue or contact [your-email@example.com]

---

**Built with ❤️ to combat vishing and protect users from phone scams**