from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import os
from models.deepfake_detector import ImprovedDeepfakeDetector
from models.intent_analyzer import IntentAnalyzer
from utils.audio_preprocessor import AudioPreprocessor

app = FastAPI(title="EchoCheck AI Service - Enhanced")

# CORS for Node.js backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models (loaded once at startup)
deepfake_detector = ImprovedDeepfakeDetector()
intent_analyzer = IntentAnalyzer()
audio_preprocessor = AudioPreprocessor()

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Main endpoint: Analyzes audio for deepfake + scam intent
    Context-aware detection for sophisticated AI voices
    """
    try:
        print("\n" + "="*60)
        print(f"📁 Analyzing file: {file.filename}")
        print("="*60)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Step 1: Preprocess audio
        processed_audio = audio_preprocessor.process(tmp_path)
        print("✅ Audio preprocessed")
        
        # Step 2: Advanced Deepfake Detection
        deepfake_result = deepfake_detector.detect(processed_audio)
        print(f"\n🤖 DEEPFAKE DETECTION RESULT:")
        print(f"   Is AI: {deepfake_result['is_deepfake']}")
        print(f"   Confidence: {deepfake_result['confidence']:.3f}")
        print(f"   Method: {deepfake_result['method']}")
        
        # Step 3: Speech-to-Text
        transcript = audio_preprocessor.transcribe(tmp_path)
        print(f"\n📝 Transcript: {transcript[:100]}...")
        
        # Step 4: Intent Analysis (Scam Detection)
        intent_result = intent_analyzer.analyze(transcript)
        print(f"\n🚨 SCAM DETECTION RESULT:")
        print(f"   Is Scam: {intent_result['is_scam']}")
        print(f"   Confidence: {intent_result['confidence']:.3f}")
        print(f"   Indicators: {len(intent_result['indicators'])} red flags")
        
        # Step 5: Context-Aware Risk Level Calculation
        risk_level = calculate_context_aware_risk(deepfake_result, intent_result)
        print(f"\n⚠️  FINAL RISK LEVEL: {risk_level}")
        
        # Step 6: Determine Voice Type
        voice_type = determine_voice_type_context_aware(deepfake_result, intent_result)
        print(f"🎭 Voice Type: {voice_type}")
        
        # Cleanup
        os.unlink(tmp_path)
        
        print("\n" + "="*60)
        print("✅ Analysis complete!")
        print("="*60 + "\n")
        
        return {
            "is_deepfake": deepfake_result["is_deepfake"],
            "deepfake_confidence": deepfake_result["confidence"],
            "deepfake_details": deepfake_result.get("details", {}),
            "is_scam": intent_result["is_scam"],
            "scam_confidence": intent_result["confidence"],
            "transcript": transcript,
            "scam_indicators": intent_result["indicators"],
            "risk_level": risk_level,
            "voice_type": voice_type,
            "detection_method": deepfake_result.get("method", "unknown")
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def calculate_context_aware_risk(deepfake_result, intent_result):
    """
    Context-aware risk calculation
    Catches sophisticated AI voices when combined with scam content
    """
    df_score = deepfake_result["confidence"]
    df_detected = deepfake_result["is_deepfake"]
    scam_score = intent_result["confidence"]
    scam_detected = intent_result["is_scam"]
    
    print(f"\n📊 Risk Calculation:")
    print(f"   Deepfake Score: {df_score:.3f} (Detected: {df_detected})")
    print(f"   Scam Score: {scam_score:.3f} (Detected: {scam_detected})")
    
    # CRITICAL: Very high scam score (90%+)
    if scam_score > 0.90:
        print("   🔴 Scam score >90% → CRITICAL")
        return "CRITICAL"
    
    # CRITICAL: Context - Moderate AI (30%+) + High Scam (70%+)
    # Catches sophisticated AI scam calls
    if df_score > 0.30 and scam_score > 0.70:
        print("   🔴 AI suspicion + Scam content → CRITICAL")
        return "CRITICAL"
    
    # CRITICAL: Both AI and scam officially detected
    if df_detected and scam_detected:
        combined = (df_score * 0.60 + scam_score * 0.40)
        combined = min(combined * 1.5, 1.0)
        print(f"   🔴 Both AI + Scam detected → Combined: {combined:.3f}")
        return "CRITICAL"
    
    # HIGH: Scam detected with any AI suspicion
    if scam_detected and df_score > 0.20:
        print(f"   🟠 Scam + AI suspicion → HIGH")
        return "HIGH"
    
    # HIGH: Strong AI detection (65%+)
    if df_score > 0.65:
        combined = (df_score * 0.75 + scam_score * 0.25)
        print(f"   🟠 Strong AI detection → Combined: {combined:.3f}")
        if combined > 0.70:
            return "CRITICAL"
        else:
            return "HIGH"
    
    # MEDIUM: Moderate AI detection (45-65%)
    if df_score > 0.45:
        combined = (df_score * 0.65 + scam_score * 0.35)
        print(f"   🟡 Moderate AI detection → Combined: {combined:.3f}")
        if combined > 0.60:
            return "HIGH"
        else:
            return "MEDIUM"
    
    # MEDIUM: Scam detected (even without AI)
    if scam_detected:
        print(f"   🟡 Scam detected → MEDIUM")
        return "MEDIUM"
    
    # LOW: Nothing detected
    print(f"   🟢 No threats → LOW")
    return "LOW"

def determine_voice_type_context_aware(deepfake_result, intent_result):
    """
    Context-aware voice type determination
    Catches sophisticated AI voices based on context
    """
    df_score = deepfake_result["confidence"]
    df_detected = deepfake_result["is_deepfake"]
    scam_detected = intent_result["is_scam"]
    scam_score = intent_result["confidence"]
    
    print(f"\n🎭 Determining Voice Type:")
    print(f"   AI: {df_detected} ({df_score:.3f})")
    print(f"   Scam: {scam_detected} ({scam_score:.3f})")
    
    # PRIORITY 1: Context - Moderate AI (30%+) + High Scam (70%+)
    # Catches sophisticated AI voices that slip through detection
    if df_score > 0.30 and scam_score > 0.70:
        print("   → AI_VOICE_SCAM (Context: AI suspicion + scam content)")
        return "AI_VOICE_SCAM"
    
    # PRIORITY 2: Context - Moderate AI (35%+) + Perfect Scam (95%+)
    # Very high confidence it's AI reading a scam script
    if df_score > 0.25 and scam_score > 0.95:
        print("   → AI_VOICE_SCAM (Context: AI + perfect scam script)")
        return "AI_VOICE_SCAM"
    
    # PRIORITY 3: Both officially detected with strong AI
    if df_detected and scam_detected and df_score > 0.60:
        print("   → AI_VOICE_SCAM (Both detected with strong AI)")
        return "AI_VOICE_SCAM"
    
    # PRIORITY 4: High AI detection (65%+)
    if df_score > 0.65:
        print("   → AI_VOICE_CLONING (High AI detection)")
        return "AI_VOICE_CLONING"
    
    # PRIORITY 5: AI officially detected
    if df_detected:
        print("   → SYNTHETIC_VOICE (AI detected)")
        return "SYNTHETIC_VOICE"
    
    # PRIORITY 6: Just scam (human scammer)
    if scam_detected:
        print("   → HUMAN_SCAM (Scam with human voice)")
        return "HUMAN_SCAM"
    
    # PRIORITY 7: Nothing detected
    print("   → LEGITIMATE (Clean)")
    return "LEGITIMATE"

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": True,
        "detection_mode": "context_aware",
        "version": "3.0"
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🛡️  EchoCheck AI Service - CONTEXT-AWARE MODE")
    print("="*60)
    print("✅ Optimized for sophisticated AI voice detection")
    print("✅ Context-aware: Combines AI + scam signals")
    print("✅ Reduces false positives on normal voices")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
