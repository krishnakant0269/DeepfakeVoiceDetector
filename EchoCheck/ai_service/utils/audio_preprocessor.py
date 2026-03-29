import librosa
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import os
import traceback

class AudioPreprocessor:
    """Handles audio loading, resampling, and transcription"""
    
    def __init__(self):
        # Use absolute path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "models", "vosk-model-small-en-us-0.15")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at: {model_path}")
        
        print(f"Loading Vosk model from: {model_path}")
        self.vosk_model = Model(model_path)
    
    def process(self, audio_path, target_sr=16000):
        """
        Loads and preprocesses audio
        
        Returns:
            numpy array of audio samples
        """
        try:
            print(f"Loading audio from: {audio_path}")
            print(f"File size: {os.path.getsize(audio_path)} bytes")
            
            # Try loading with librosa (requires ffmpeg)
            audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)
            
            print(f"Loaded audio: {len(audio)} samples at {sr}Hz")
            
            # Normalize
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            else:
                print("Warning: Audio is silent!")
                audio = np.zeros(target_sr)
            
            return audio
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            print(f"Full traceback:")
            traceback.print_exc()
            # Return 1 second of silence if processing fails
            return np.zeros(target_sr)
    
    def transcribe(self, audio_path):
        """
        Converts speech to text using Vosk
        
        Returns:
            transcript string
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_path):
                print(f"Audio file not found: {audio_path}")
                return "No audio detected"
            
            print(f"Transcribing: {audio_path}")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            if len(audio) == 0:
                return "Empty audio file"
            
            print(f"Audio loaded for transcription: {len(audio)} samples")
            
            # Convert to 16-bit PCM
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Create recognizer
            rec = KaldiRecognizer(self.vosk_model, 16000)
            rec.SetWords(True)
            
            transcript = ""
            
            # Process audio in chunks
            chunk_size = 4000
            for i in range(0, len(audio_int16), chunk_size):
                chunk = audio_int16[i:i+chunk_size].tobytes()
                
                if rec.AcceptWaveform(chunk):
                    result = json.loads(rec.Result())
                    transcript += result.get("text", "") + " "
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            transcript += final_result.get("text", "")
            
            final_transcript = transcript.strip()
            
            if not final_transcript:
                return "No speech detected in audio"
            
            print(f"Transcript: {final_transcript}")
            return final_transcript
            
        except Exception as e:
            print(f"Transcription error: {e}")
            traceback.print_exc()
            return "Transcription failed"