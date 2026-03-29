# EchoCheck Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                     (React Frontend)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Audio        │  │ Results      │  │ Scan         │         │
│  │ Recorder     │  │ Dashboard    │  │ History      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                │
│                   (Node.js + Express)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Upload       │  │ Auth         │  │ History      │         │
│  │ Handler      │  │ Middleware   │  │ Manager      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────┬───────────────────────────────┬─────────────────┘
                │                               │
                │ Audio File                    │ Metadata
                ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────┐
│      AI PROCESSING            │   │       DATABASE            │
│    (Python FastAPI)           │   │      (MongoDB)            │
│                               │   │                           │
│  ┌─────────────────────────┐ │   │  ┌─────────────────────┐ │
│  │  PILLAR A:              │ │   │  │ • User Profiles      │ │
│  │  Deepfake Detection     │ │   │  │ • Scan History       │ │
│  │  ┌──────────────────┐   │ │   │  │ • Scam Patterns      │ │
│  │  │ Wav2Vec2/RawNet2 │   │ │   │  │ • Analytics          │ │
│  │  │ Spectral Analysis│   │ │   │  └─────────────────────┘ │
│  │  └──────────────────┘   │ │   │                           │
│  └─────────────────────────┘ │   └───────────────────────────┘
│                               │
│  ┌─────────────────────────┐ │
│  │  PILLAR B:              │ │
│  │  Intent Analysis        │ │
│  │  ┌──────────────────┐   │ │
│  │  │ Vosk (STT)       │   │ │
│  │  │ BERT/LLM         │   │ │
│  │  │ Pattern Matching │   │ │
│  │  └──────────────────┘   │ │
│  └─────────────────────────┘ │
└───────────────────────────────┘
```

## Data Flow

### 1. Audio Upload Flow

```
User Records Audio
       ↓
React MediaRecorder API captures audio blob
       ↓
POST /api/audio/analyze (with FormData)
       ↓
Multer middleware saves to /uploads
       ↓
Node.js forwards to Python AI service
       ↓
[AI Processing - see below]
       ↓
Node.js receives AI results
       ↓
Save to MongoDB
       ↓
Return results to React
       ↓
Display in ResultsCard component
```

### 2. AI Processing Pipeline

```
Audio File Input (.wav, .mp3, etc.)
       ↓
┌──────────────────────────────┐
│  Audio Preprocessing         │
│  • Load with Librosa         │
│  • Resample to 16kHz         │
│  • Normalize amplitude       │
│  • Trim silence              │
└──────────────┬───────────────┘
               │
               ├─────────────────────────┬──────────────────────┐
               ▼                         ▼                      ▼
    ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
    │ PILLAR A:        │   │ Speech-to-Text   │   │ PILLAR B:        │
    │ Deepfake Check   │   │ (Vosk)           │   │ Intent Analysis  │
    │                  │   │                  │   │                  │
    │ Spectral         │   │ Audio → Text     │   │ BERT            │
    │ Analysis:        │   │                  │   │ Classification   │
    │ • High-freq      │   │ "Hello, this is  │   │                  │
    │   energy ratio   │   │  your bank..."   │   │ Pattern         │
    │ • Formants       │   │                  │   │ Matching:        │
    │ • Phase          │   │                  │   │ • Urgency words  │
    │   coherence      │   │                  │   │ • OTP requests   │
    │                  │   │                  │   │ • Authority      │
    │ OR               │   │                  │   │   impersonation  │
    │                  │   │                  │   │                  │
    │ Neural Model:    │   │                  │   │ Scam DB lookup   │
    │ Wav2Vec2         │   │                  │   │                  │
    └─────┬────────────┘   └─────────┬────────┘   └─────┬────────────┘
          │                          │                    │
          ▼                          ▼                    ▼
    is_deepfake: bool          transcript           is_scam: bool
    confidence: 0.87                                confidence: 0.92
                               └────────────┬───────┘
                                            ▼
                               ┌────────────────────────┐
                               │  Risk Calculation      │
                               │  weighted_score =      │
                               │   (0.6 × deepfake) +   │
                               │   (0.4 × scam)         │
                               │                        │
                               │  → CRITICAL/HIGH/      │
                               │     MEDIUM/LOW         │
                               └────────────────────────┘
```

## Key Technologies Explained

### Why These Tools?

#### 1. **Wav2Vec2 (Deepfake Detection)**
- **What it does**: Learns audio representations from raw waveforms
- **Why use it**: Can detect subtle "neural artifacts" that humans miss
- **Alternatives**: RawNet2 (faster), HuBERT, WavLM

#### 2. **Spectral Analysis**
- **What it does**: Analyzes frequency content of audio
- **Why use it**: Deepfakes often fail at high frequencies (sibilants, breathing)
- **Key features**:
  - High-frequency energy ratio
  - Formant stability
  - Phase coherence

#### 3. **Vosk (Speech-to-Text)**
- **What it does**: Converts speech to text offline
- **Why use it**: Fast, private, no API costs
- **Alternatives**: Whisper (more accurate but slower), Google STT (cloud-based)

#### 4. **BERT (Intent Analysis)**
- **What it does**: Understands semantic meaning of text
- **Why use it**: Detects scam intent even with rephrased scripts
- **How we use it**: Zero-shot classification for scam categories

## Security Considerations

### 1. Audio Privacy
```javascript
// Never store raw audio permanently
// Process → Analyze → Delete

fs.unlinkSync(req.file.path);  // Delete after analysis
```

### 2. Rate Limiting
```javascript
// Prevent abuse
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10 // 10 requests per window
});

app.use('/api/audio/analyze', limiter);
```

### 3. Authentication
```javascript
// JWT token verification
const auth = async (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  // Verify token...
};
```

## Scalability Strategies

### Horizontal Scaling

```yaml
# docker-compose-scaled.yml
services:
  ai-service:
    image: echocheck-ai
    deploy:
      replicas: 3  # 3 AI instances
    
  backend:
    image: echocheck-backend
    deploy:
      replicas: 2  # 2 API instances
    
  nginx:
    image: nginx
    # Load balance across instances
```

### Caching Strategy

```javascript
// Cache common scam patterns
const Redis = require('redis');
const client = Redis.createClient();

// Before expensive AI call
const cached = await client.get(`transcript:${hash}`);
if (cached) return JSON.parse(cached);

// After analysis
await client.setEx(`transcript:${hash}`, 3600, JSON.stringify(result));
```

## Performance Optimization

### 1. Audio Compression
```javascript
// Compress before sending to AI service
const ffmpeg = require('fluent-ffmpeg');

ffmpeg(inputPath)
  .audioCodec('libopus')
  .audioBitrate('32k')
  .save(outputPath);
```

### 2. Async Processing
```javascript
// For long files, use job queue
const Bull = require('bull');
const audioQueue = new Bull('audio-analysis');

// Add job
await audioQueue.add({ audioPath, userId });

// Process in background
audioQueue.process(async (job) => {
  // Run AI analysis
  // Update database when done
});
```

## Monitoring & Logging

### Key Metrics to Track

1. **Detection Accuracy**
   - False positive rate
   - False negative rate
   - Precision/Recall

2. **Performance**
   - Average processing time
   - AI service latency
   - Queue depth

3. **Usage**
   - Scans per day
   - Risk level distribution
   - Most common scam types

```javascript
// Example logging
const winston = require('winston');

logger.info('Analysis complete', {
  scanId: scanRecord._id,
  processingTime: endTime - startTime,
  riskLevel: result.risk_level,
  deepfakeDetected: result.is_deepfake
});
```

## Common Pitfalls & Solutions

### 1. Audio Format Issues
**Problem**: Different browsers record in different formats
**Solution**: Server-side conversion with FFmpeg

### 2. Model Memory Issues
**Problem**: Large models crash on small servers
**Solution**: Use quantized models or model sharding

### 3. False Positives
**Problem**: Legitimate calls flagged as scams
**Solution**: Ensemble approach + confidence thresholds

## Future Enhancements

1. **Real-time Analysis**: WebRTC for live call monitoring
2. **Multi-language Support**: Vosk models for other languages
3. **Voice Biometrics**: Verify caller identity
4. **Blockchain Audit Trail**: Immutable scan records
5. **Mobile SDK**: Native apps for Android/iOS

## Resources

- [ASVspoof Dataset](https://www.asvspoof.org/)
- [Wav2Vec2 Paper](https://arxiv.org/abs/2006.11477)
- [Vosk Models](https://alphacephei.com/vosk/models)
- [Vishing Statistics](https://www.ftc.gov/reports/consumer-sentinel-network)
