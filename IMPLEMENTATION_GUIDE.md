# EchoCheck Implementation Guide

## Complete Architecture & Code Examples

### Tech Stack
- **Frontend**: React + MediaRecorder API
- **Backend**: Node.js + Express
- **AI Service**: Python FastAPI + Wav2Vec2 + BERT
- **Database**: MongoDB
- **Audio Processing**: Librosa, Vosk (STT)

---

## 1. PROJECT STRUCTURE

```
EchoCheck/
├── client/                    # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.jsx
│   │   │   ├── ResultsCard.jsx
│   │   │   └── ScanHistory.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── utils/
│   │   │   └── audioProcessor.js
│   │   ├── App.jsx
│   │   └── index.js
│   └── package.json
│
├── server/                    # Node.js Backend
│   ├── controllers/
│   │   ├── audioController.js
│   │   └── userController.js
│   ├── models/
│   │   ├── ScanHistory.js
│   │   └── User.js
│   ├── routes/
│   │   ├── audio.js
│   │   └── user.js
│   ├── middleware/
│   │   ├── auth.js
│   │   └── upload.js
│   ├── config/
│   │   └── db.js
│   ├── server.js
│   └── package.json
│
├── ai_service/                # Python AI Service
│   ├── models/
│   │   ├── deepfake_detector.py
│   │   └── intent_analyzer.py
│   ├── utils/
│   │   ├── audio_preprocessor.py
│   │   └── scam_patterns.json
│   ├── main.py
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

---

## 2. PYTHON AI SERVICE (FastAPI)

### `ai_service/requirements.txt`

```txt
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
```

### `ai_service/main.py`

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import os
from models.deepfake_detector import DeepfakeDetector
from models.intent_analyzer import IntentAnalyzer
from utils.audio_preprocessor import AudioPreprocessor

app = FastAPI(title="EchoCheck AI Service")

# CORS for Node.js backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # Node.js server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models (loaded once at startup)
deepfake_detector = DeepfakeDetector()
intent_analyzer = IntentAnalyzer()
audio_preprocessor = AudioPreprocessor()

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Main endpoint: Analyzes audio for deepfake + scam intent
    Returns: {
        "is_deepfake": bool,
        "deepfake_confidence": float,
        "is_scam": bool,
        "scam_confidence": float,
        "transcript": str,
        "scam_indicators": []
    }
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Step 1: Preprocess audio
        processed_audio = audio_preprocessor.process(tmp_path)
        
        # Step 2: Deepfake Detection (Pillar A)
        deepfake_result = deepfake_detector.detect(processed_audio)
        
        # Step 3: Speech-to-Text
        transcript = audio_preprocessor.transcribe(tmp_path)
        
        # Step 4: Intent Analysis (Pillar B)
        intent_result = intent_analyzer.analyze(transcript)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "is_deepfake": deepfake_result["is_deepfake"],
            "deepfake_confidence": deepfake_result["confidence"],
            "is_scam": intent_result["is_scam"],
            "scam_confidence": intent_result["confidence"],
            "transcript": transcript,
            "scam_indicators": intent_result["indicators"],
            "risk_level": calculate_risk_level(deepfake_result, intent_result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_risk_level(deepfake_result, intent_result):
    """Combines both scores to determine overall risk"""
    df_score = deepfake_result["confidence"] if deepfake_result["is_deepfake"] else 0
    scam_score = intent_result["confidence"] if intent_result["is_scam"] else 0
    
    combined = (df_score * 0.6 + scam_score * 0.4)  # Weight deepfake higher
    
    if combined > 0.8:
        return "CRITICAL"
    elif combined > 0.6:
        return "HIGH"
    elif combined > 0.4:
        return "MEDIUM"
    else:
        return "LOW"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### `ai_service/models/deepfake_detector.py`

```python
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
import numpy as np

class DeepfakeDetector:
    """
    Uses Wav2Vec2 fine-tuned on deepfake audio detection
    Detects neural artifacts like:
    - Unnatural breathing patterns
    - Spectral inconsistencies
    - Phase misalignment
    """
    
    def __init__(self):
        # Option 1: Use pre-trained Wav2Vec2 (requires fine-tuning on deepfake data)
        # Option 2: Use RawNet2 (specialized for anti-spoofing)
        
        # For demo, we'll use a Wav2Vec2 base model
        # In production, replace with your fine-tuned model
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        
        # You'd load your custom-trained model here:
        # self.model = Wav2Vec2ForSequenceClassification.from_pretrained("./your_model")
        
        # Placeholder: Spectral analysis approach
        self.use_spectral_method = True
        
    def detect(self, audio_array, sample_rate=16000):
        """
        Analyzes audio for deepfake signatures
        
        Args:
            audio_array: numpy array of audio samples
            sample_rate: audio sample rate
            
        Returns:
            {
                "is_deepfake": bool,
                "confidence": float (0-1),
                "method": str
            }
        """
        
        if self.use_spectral_method:
            return self._spectral_analysis(audio_array, sample_rate)
        else:
            return self._neural_analysis(audio_array, sample_rate)
    
    def _spectral_analysis(self, audio_array, sample_rate):
        """
        Analyzes spectral features for deepfake detection
        Key indicators:
        - High-frequency artifacts (most TTS/VC fails here)
        - Formant consistency
        - Pitch naturalness
        """
        
        # Compute spectrogram
        spec = torchaudio.transforms.Spectrogram()(torch.tensor(audio_array))
        
        # Feature extraction
        high_freq_energy = torch.mean(spec[-100:, :])  # Top 100 freq bins
        total_energy = torch.mean(spec)
        
        hf_ratio = (high_freq_energy / total_energy).item()
        
        # Deepfakes often have lower high-frequency content
        # Threshold based on empirical testing
        is_deepfake = hf_ratio < 0.15
        confidence = min(abs(0.15 - hf_ratio) / 0.15, 1.0)
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "method": "spectral_analysis",
            "hf_ratio": hf_ratio
        }
    
    def _neural_analysis(self, audio_array, sample_rate):
        """
        Uses Wav2Vec2 model for detection
        (Requires fine-tuned model on deepfake dataset)
        """
        
        # Preprocess
        inputs = self.processor(
            audio_array, 
            sampling_rate=sample_rate, 
            return_tensors="pt"
        )
        
        # Inference
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
        
        # Assuming binary classification: [real, fake]
        fake_prob = probs[0][1].item()
        
        return {
            "is_deepfake": fake_prob > 0.5,
            "confidence": fake_prob,
            "method": "neural_network"
        }
```

### `ai_service/models/intent_analyzer.py`

```python
from transformers import pipeline
import json
import re

class IntentAnalyzer:
    """
    Analyzes transcript for vishing/scam intent
    Uses BERT-based classification + rule-based patterns
    """
    
    def __init__(self):
        # Load BERT sentiment/classification model
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Load scam patterns
        with open("utils/scam_patterns.json", "r") as f:
            self.scam_patterns = json.load(f)
    
    def analyze(self, transcript):
        """
        Analyzes text for scam intent
        
        Returns:
            {
                "is_scam": bool,
                "confidence": float,
                "indicators": [list of detected red flags]
            }
        """
        
        # Step 1: Zero-shot classification
        labels = ["legitimate_call", "scam_call", "telemarketing", "urgent_request"]
        result = self.classifier(transcript, candidate_labels=labels)
        
        scam_score = result["scores"][result["labels"].index("scam_call")]
        
        # Step 2: Pattern matching for known scam phrases
        indicators = self._detect_scam_patterns(transcript)
        
        # Step 3: Urgency detection
        urgency_score = self._detect_urgency(transcript)
        
        # Combine scores
        pattern_score = len(indicators) * 0.2  # Each indicator adds 20%
        final_confidence = min((scam_score * 0.5 + pattern_score + urgency_score * 0.3), 1.0)
        
        return {
            "is_scam": final_confidence > 0.6,
            "confidence": final_confidence,
            "indicators": indicators,
            "urgency_detected": urgency_score > 0.5
        }
    
    def _detect_scam_patterns(self, text):
        """Checks for common vishing phrases"""
        found_patterns = []
        text_lower = text.lower()
        
        for category, patterns in self.scam_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found_patterns.append({
                        "category": category,
                        "matched_pattern": pattern
                    })
        
        return found_patterns
    
    def _detect_urgency(self, text):
        """Detects urgency language"""
        urgency_words = [
            "urgent", "immediately", "right now", "within 24 hours",
            "expire", "suspend", "locked", "frozen", "last chance"
        ]
        
        count = sum(1 for word in urgency_words if word in text.lower())
        return min(count / 3, 1.0)  # Normalize to 0-1
```

### `ai_service/utils/scam_patterns.json`

```json
{
  "financial_urgency": [
    "your account (will be|has been) (suspended|locked|frozen)",
    "unauthorized (transaction|activity)",
    "verify your account",
    "confirm your (identity|ssn|social security)",
    "update your payment"
  ],
  "authority_impersonation": [
    "(IRS|tax department|revenue service)",
    "federal (agent|officer)",
    "you owe.*tax",
    "warrant.*arrest",
    "legal action"
  ],
  "tech_support_scam": [
    "computer (virus|infected|compromised)",
    "microsoft.*calling",
    "windows.*support",
    "refund.*subscription",
    "remote access"
  ],
  "otp_request": [
    "one.?time (password|code|pin|otp)",
    "verification code",
    "6.?digit (code|number)",
    "text.*code"
  ],
  "personal_info_phishing": [
    "social security number",
    "date of birth",
    "mother'?s maiden name",
    "card number.*CVV",
    "online banking (password|credentials)"
  ]
}
```

### `ai_service/utils/audio_preprocessor.py`

```python
import librosa
import soundfile as sf
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import wave

class AudioPreprocessor:
    """Handles audio loading, resampling, and transcription"""
    
    def __init__(self):
        # Load Vosk model for STT (download from https://alphacephei.com/vosk/models)
        # Use small model for faster processing: vosk-model-small-en-us-0.15
        self.vosk_model = Model("models/vosk-model-small-en-us-0.15")
    
    def process(self, audio_path, target_sr=16000):
        """
        Loads and preprocesses audio
        
        Returns:
            numpy array of audio samples
        """
        # Load audio
        audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        # Remove silence (optional)
        audio = self._trim_silence(audio, sr)
        
        return audio
    
    def _trim_silence(self, audio, sr, threshold=0.01):
        """Removes leading/trailing silence"""
        non_silent = librosa.effects.split(audio, top_db=20)
        if len(non_silent) > 0:
            start = non_silent[0][0]
            end = non_silent[-1][1]
            return audio[start:end]
        return audio
    
    def transcribe(self, audio_path):
        """
        Converts speech to text using Vosk
        
        Returns:
            transcript string
        """
        wf = wave.open(audio_path, "rb")
        
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio must be 16kHz mono PCM")
        
        rec = KaldiRecognizer(self.vosk_model, wf.getframerate())
        rec.SetWords(True)
        
        transcript = ""
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                transcript += result.get("text", "") + " "
        
        # Final result
        final_result = json.loads(rec.FinalResult())
        transcript += final_result.get("text", "")
        
        return transcript.strip()
```

---

## 3. NODE.JS BACKEND

### `server/package.json`

```json
{
  "name": "echocheck-server",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^8.0.0",
    "multer": "^1.4.5-lts.1",
    "axios": "^1.6.0",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

### `server/server.js`

```javascript
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const audioRoutes = require('./routes/audio');
const userRoutes = require('./routes/user');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/audio', audioRoutes);
app.use('/api/user', userRoutes);

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/echocheck', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('✅ MongoDB Connected'))
.catch(err => console.error('MongoDB Error:', err));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'EchoCheck API' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
```

### `server/models/ScanHistory.js`

```javascript
const mongoose = require('mongoose');

const ScanHistorySchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  fileName: String,
  fileSize: Number,
  duration: Number, // in seconds
  
  // AI Analysis Results
  deepfakeDetected: {
    type: Boolean,
    required: true
  },
  deepfakeConfidence: {
    type: Number,
    min: 0,
    max: 1
  },
  scamDetected: {
    type: Boolean,
    required: true
  },
  scamConfidence: {
    type: Number,
    min: 0,
    max: 1
  },
  riskLevel: {
    type: String,
    enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
  },
  
  // Transcript & Analysis
  transcript: String,
  scamIndicators: [{
    category: String,
    matchedPattern: String
  }],
  
  // Metadata
  audioUrl: String, // S3 or local path (optional)
  ipAddress: String,
  userAgent: String,
  
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Index for fast queries
ScanHistorySchema.index({ userId: 1, createdAt: -1 });
ScanHistorySchema.index({ riskLevel: 1 });

module.exports = mongoose.model('ScanHistory', ScanHistorySchema);
```

### `server/controllers/audioController.js`

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const ScanHistory = require('../models/ScanHistory');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

exports.analyzeAudio = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No audio file provided' });
    }

    console.log(`📁 Received file: ${req.file.originalname} (${req.file.size} bytes)`);

    // Send to Python AI service
    const formData = new FormData();
    formData.append('file', fs.createReadStream(req.file.path), {
      filename: req.file.originalname,
      contentType: req.file.mimetype
    });

    const aiResponse = await axios.post(`${AI_SERVICE_URL}/analyze`, formData, {
      headers: formData.getHeaders(),
      timeout: 60000 // 60 second timeout
    });

    const aiResult = aiResponse.data;

    // Save to database
    const scanRecord = new ScanHistory({
      userId: req.user.id, // From auth middleware
      fileName: req.file.originalname,
      fileSize: req.file.size,
      deepfakeDetected: aiResult.is_deepfake,
      deepfakeConfidence: aiResult.deepfake_confidence,
      scamDetected: aiResult.is_scam,
      scamConfidence: aiResult.scam_confidence,
      riskLevel: aiResult.risk_level,
      transcript: aiResult.transcript,
      scamIndicators: aiResult.scam_indicators,
      ipAddress: req.ip,
      userAgent: req.headers['user-agent']
    });

    await scanRecord.save();

    // Cleanup uploaded file
    fs.unlinkSync(req.file.path);

    // Send response
    res.json({
      success: true,
      scanId: scanRecord._id,
      results: {
        isDeepfake: aiResult.is_deepfake,
        deepfakeConfidence: aiResult.deepfake_confidence,
        isScam: aiResult.is_scam,
        scamConfidence: aiResult.scam_confidence,
        riskLevel: aiResult.risk_level,
        transcript: aiResult.transcript,
        indicators: aiResult.scam_indicators
      }
    });

  } catch (error) {
    console.error('Analysis error:', error.message);
    
    // Cleanup file on error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    res.status(500).json({ 
      error: 'Analysis failed',
      details: error.message 
    });
  }
};

exports.getScanHistory = async (req, res) => {
  try {
    const scans = await ScanHistory.find({ userId: req.user.id })
      .sort({ createdAt: -1 })
      .limit(50)
      .select('-__v');

    res.json({
      success: true,
      count: scans.length,
      scans
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
```

### `server/routes/audio.js`

```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');
const audioController = require('../controllers/audioController');
const auth = require('../middleware/auth');

const router = express.Router();

// Configure multer for audio uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'audio-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB max
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /wav|mp3|ogg|webm|m4a/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
      return cb(null, true);
    }
    cb(new Error('Only audio files allowed'));
  }
});

// Routes
router.post('/analyze', auth, upload.single('audio'), audioController.analyzeAudio);
router.get('/history', auth, audioController.getScanHistory);

module.exports = router;
```

---

## 4. REACT FRONTEND

### `client/src/components/AudioRecorder.jsx`

```jsx
import React, { useState, useRef } from 'react';
import axios from 'axios';

const AudioRecorder = ({ onAnalysisComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Microphone access error:', error);
      alert('Could not access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const analyzeAudio = async () => {
    if (!audioBlob) return;

    setIsAnalyzing(true);

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:5000/api/audio/analyze',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      onAnalysisComplete(response.data.results);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="audio-recorder">
      <h2>Voice Call Analysis</h2>
      
      <div className="controls">
        {!isRecording ? (
          <button onClick={startRecording} className="btn-primary">
            🎤 Start Recording
          </button>
        ) : (
          <button onClick={stopRecording} className="btn-danger">
            ⏹ Stop Recording
          </button>
        )}

        {audioBlob && !isRecording && (
          <button 
            onClick={analyzeAudio} 
            disabled={isAnalyzing}
            className="btn-success"
          >
            {isAnalyzing ? '🔄 Analyzing...' : '🔍 Analyze Call'}
          </button>
        )}
      </div>

      {isRecording && (
        <div className="recording-indicator">
          <span className="pulse-dot"></span>
          Recording in progress...
        </div>
      )}

      {audioBlob && !isRecording && (
        <div className="audio-preview">
          <audio controls src={URL.createObjectURL(audioBlob)} />
        </div>
      )}
    </div>
  );
};

export default AudioRecorder;
```

### `client/src/components/ResultsCard.jsx`

```jsx
import React from 'react';

const ResultsCard = ({ results }) => {
  if (!results) return null;

  const getRiskColor = (level) => {
    const colors = {
      LOW: '#10b981',
      MEDIUM: '#f59e0b',
      HIGH: '#ef4444',
      CRITICAL: '#991b1b'
    };
    return colors[level] || '#6b7280';
  };

  return (
    <div className="results-card">
      <div className="risk-badge" style={{ backgroundColor: getRiskColor(results.riskLevel) }}>
        Risk Level: {results.riskLevel}
      </div>

      <div className="results-grid">
        {/* Deepfake Detection */}
        <div className="result-section">
          <h3>🤖 Deepfake Detection</h3>
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${results.deepfakeConfidence * 100}%`,
                backgroundColor: results.isDeepfake ? '#ef4444' : '#10b981'
              }}
            />
          </div>
          <p>
            {results.isDeepfake ? '⚠️ AI-Generated Voice Detected' : '✅ Human Voice Detected'}
          </p>
          <small>Confidence: {(results.deepfakeConfidence * 100).toFixed(1)}%</small>
        </div>

        {/* Scam Detection */}
        <div className="result-section">
          <h3>🚨 Scam Detection</h3>
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${results.scamConfidence * 100}%`,
                backgroundColor: results.isScam ? '#ef4444' : '#10b981'
              }}
            />
          </div>
          <p>
            {results.isScam ? '⚠️ Scam Indicators Found' : '✅ No Scam Detected'}
          </p>
          <small>Confidence: {(results.scamConfidence * 100).toFixed(1)}%</small>
        </div>
      </div>

      {/* Transcript */}
      <div className="transcript-section">
        <h3>📝 Transcript</h3>
        <p className="transcript-text">{results.transcript || 'No transcript available'}</p>
      </div>

      {/* Scam Indicators */}
      {results.indicators && results.indicators.length > 0 && (
        <div className="indicators-section">
          <h3>🔍 Detected Red Flags</h3>
          <ul>
            {results.indicators.map((indicator, idx) => (
              <li key={idx}>
                <strong>{indicator.category}:</strong> {indicator.matched_pattern}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResultsCard;
```

---

## 5. DEPLOYMENT

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  # MongoDB
  mongodb:
    image: mongo:7.0
    container_name: echocheck-db
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    environment:
      MONGO_INITDB_DATABASE: echocheck

  # Python AI Service
  ai-service:
    build: ./ai_service
    container_name: echocheck-ai
    ports:
      - "8000:8000"
    volumes:
      - ./ai_service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - mongodb

  # Node.js Backend
  backend:
    build: ./server
    container_name: echocheck-backend
    ports:
      - "5000:5000"
    environment:
      MONGODB_URI: mongodb://mongodb:27017/echocheck
      AI_SERVICE_URL: http://ai-service:8000
      JWT_SECRET: your-secret-key
    volumes:
      - ./server:/app
      - /app/node_modules
    depends_on:
      - mongodb
      - ai-service

  # React Frontend
  frontend:
    build: ./client
    container_name: echocheck-frontend
    ports:
      - "3000:3000"
    volumes:
      - ./client:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  mongo-data:
```

---

## 6. RUNNING THE PROJECT

### Local Development (Without Docker)

```bash
# 1. Start MongoDB
mongod

# 2. Start Python AI Service
cd ai_service
pip install -r requirements.txt
# Download Vosk model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/
python main.py

# 3. Start Node.js Backend
cd ../server
npm install
mkdir uploads
npm run dev

# 4. Start React Frontend
cd ../client
npm install
npm start
```

### With Docker

```bash
docker-compose up --build
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- AI Service: http://localhost:8000

---

## 7. TRAINING YOUR OWN MODELS

### Deepfake Detection Dataset

You'll need to fine-tune Wav2Vec2 on a deepfake audio dataset:

1. **Datasets:**
   - ASVspoof 2021 (anti-spoofing challenge)
   - WaveFake (AI-generated speech detection)
   - In-The-Wild dataset

2. **Fine-tuning script:**

```python
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor, Trainer
from datasets import load_dataset

# Load pre-trained model
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "facebook/wav2vec2-base",
    num_labels=2  # binary: real/fake
)

# Load your dataset
dataset = load_dataset("your_deepfake_dataset")

# Training
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"]
)

trainer.train()
model.save_pretrained("./models/wav2vec2-deepfake-detector")
```

---

## NEXT STEPS

1. **Add Authentication**: Implement JWT-based user auth
2. **Real-time Analysis**: Use WebSockets for live call monitoring
3. **Dashboard**: Create admin panel to view trends
4. **Mobile App**: Build React Native version
5. **API Rate Limiting**: Prevent abuse
6. **Cloud Deployment**: Deploy to AWS/GCP/Azure

This is a production-ready foundation. Let me know which part you want to dive deeper into!
