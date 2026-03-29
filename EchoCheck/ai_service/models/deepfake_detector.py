
import torch
import torchaudio
import numpy as np
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
from scipy import signal
from scipy.stats import skew, kurtosis

class ImprovedDeepfakeDetector:
    """
    Advanced AI voice detection with 7 analysis methods
    """
    
    def __init__(self):
        print("🤖 Initializing IMPROVED Deepfake Detector...")
        print("📥 Using 7 advanced analysis methods...")
        
        working_models = ["facebook/wav2vec2-base"]
        
        self.use_ml_model = False
        
        for model_name in working_models:
            try:
                self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
                self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
                self.model.eval()
                self.use_ml_model = True
                print(f"✅ ML features loaded")
                break
            except:
                continue
        
        print("✅ Advanced detection ready")
    
    def detect(self, audio_array, sample_rate=16000):
        """Detect AI voices with improved accuracy"""
        return self._advanced_detection(audio_array, sample_rate)
    
    def _advanced_detection(self, audio_array, sample_rate):
        """7-method advanced detection"""
        print("🔍 Running ADVANCED 7-method detection...")
        
        try:
            # 1. Improved Spectral (accounts for recording quality)
            spectral_score = self._improved_spectral(audio_array, sample_rate)
            print(f"  📊 Spectral: {spectral_score:.3f}")
            
            # 2. Spectral Flux (transition smoothness)
            flux_score = self._spectral_flux(audio_array)
            print(f"  🌊 Flux: {flux_score:.3f}")
            
            # 3. Harmonic-Noise Ratio (cleanliness)
            hnr_score = self._harmonic_noise_ratio(audio_array)
            print(f"  🎵 HNR: {hnr_score:.3f}")
            
            # 4. Improved MFCC
            mfcc_score = self._improved_mfcc(audio_array, sample_rate)
            print(f"  📈 MFCC: {mfcc_score:.3f}")
            
            # 5. Improved Pitch
            pitch_score = self._improved_pitch(audio_array, sample_rate)
            print(f"  🎼 Pitch: {pitch_score:.3f}")
            
            # 6. ZCR
            zcr_score = self._zcr(audio_array)
            print(f"  ⚡ ZCR: {zcr_score:.3f}")
            
            # 7. Energy
            energy_score = self._energy(audio_array)
            print(f"  ⚡ Energy: {energy_score:.3f}")
            
            # Weighted combination (prioritize new methods)
            combined_score = (
                spectral_score * 0.18 +
                flux_score * 0.22 +
                hnr_score * 0.22 +
                mfcc_score * 0.15 +
                pitch_score * 0.15 +
                zcr_score * 0.04 +
                energy_score * 0.04
            )
            
            print(f"  🎯 Combined: {combined_score:.3f}")
            
            base_threshold = 0.65  # Standard detection
            sensitive_threshold = 0.30  # Context-aware detection

             # Check if we should use sensitive threshold
            use_sensitive = False

            # Condition 1: Multiple methods moderately high (50%+)
            moderate_count = sum([
                spectral_score > 0.50,
                flux_score > 0.50,
                hnr_score > 0.50,
                mfcc_score > 0.50,
                pitch_score > 0.50
            ])

            if moderate_count >= 3:
                use_sensitive = True
                print(f"  ⚠️  {moderate_count} methods >50% - using sensitive threshold")

            # Condition 2: Spectral + another method both high
            if spectral_score > 0.50 and (flux_score > 0.50 or hnr_score > 0.50 or mfcc_score > 0.50):
                use_sensitive = True
                print(f"  ⚠️  Spectral + secondary evidence - using sensitive threshold")

            # Choose threshold
            threshold = sensitive_threshold if use_sensitive else base_threshold
            print(f"  🎯 Using threshold: {threshold}")
            
            
            # Strong consensus lowers threshold
            strong_count = sum([
                flux_score > 0.70,
                hnr_score > 0.70,
                mfcc_score > 0.70,
                pitch_score > 0.70
            ])
            
            if strong_count >= 3:
                threshold = 0.55
                combined_score = min(combined_score * 1.15, 1.0)
                print(f"  ⚠️  {strong_count} strong - boosted!")
            
            is_deepfake = combined_score > threshold
            
            print(f"  {'🤖 AI' if is_deepfake else '👤 Human'}")
            
            return {
                "is_deepfake": is_deepfake,
                "confidence": combined_score,
                "method": "advanced_7method",
                "details": {
                    "spectral": round(spectral_score, 3),
                    "flux": round(flux_score, 3),
                    "hnr": round(hnr_score, 3),
                    "mfcc": round(mfcc_score, 3),
                    "pitch": round(pitch_score, 3),
                    "zcr": round(zcr_score, 3),
                    "energy": round(energy_score, 3)
                }
            }
            
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return {"is_deepfake": False, "confidence": 0.3, "method": "error", "details": {}}
    
    def _improved_spectral(self, audio_array, sample_rate):
        """Improved spectral considering mid+high frequencies"""
        try:
            spec = torchaudio.transforms.Spectrogram()(torch.tensor(audio_array))
            total = torch.mean(spec)
            
            if total == 0:
                return 0.40
            
            bins = spec.shape[0]
            low_end = int(bins * 0.25)
            mid_end = int(bins * 0.75)
            
            mid_energy = torch.mean(spec[low_end:mid_end, :])
            high_energy = torch.mean(spec[mid_end:, :])
            
            mid_ratio = (mid_energy / total).item()
            high_ratio = (high_energy / total).item()
            
            # Combined ratio (AI lacks both)
            combined = high_ratio * 0.6 + mid_ratio * 0.4
            
            if combined < 0.08:
                return 0.85
            elif combined < 0.12:
                return 0.60
            elif combined < 0.16:
                return 0.35
            elif combined < 0.20:
                return 0.20
            else:
                return 0.10
        except:
            return 0.40
    
    def _spectral_flux(self, audio_array):
        """Spectral flux - AI has smoother transitions"""
        try:
            spec = librosa.stft(audio_array)
            spec_mag = np.abs(spec)
            flux = np.sqrt(np.sum(np.diff(spec_mag, axis=1)**2, axis=0))
            flux_std = np.std(flux)
            
            if flux_std < 0.08:
                return 0.80
            elif flux_std < 0.12:
                return 0.55
            elif flux_std < 0.16:
                return 0.30
            else:
                return 0.12
        except:
            return 0.40
    
    def _harmonic_noise_ratio(self, audio_array):
        """HNR - AI voices are too clean"""
        try:
            harmonic, percussive = librosa.effects.hpss(audio_array)
            harm_energy = np.sum(harmonic**2)
            perc_energy = np.sum(percussive**2)
            
            if perc_energy == 0:
                return 0.90
            
            hnr = 10 * np.log10(harm_energy / perc_energy)
            
            # Real human: 5-20 dB, AI: >20 or <3
            if hnr > 25 or hnr < 2:
                return 0.80
            elif hnr > 20 or hnr < 4:
                return 0.55
            elif hnr > 18 or hnr < 5:
                return 0.30
            else:
                return 0.12
        except:
            return 0.40
    
    def _improved_mfcc(self, audio_array, sample_rate):
        """MFCC with statistical features"""
        try:
            mfccs = librosa.feature.mfcc(y=audio_array, sr=sample_rate, n_mfcc=13)
            variance = np.mean(np.var(mfccs, axis=1))
            
            if variance < 60:
                return 0.75
            elif variance < 120:
                return 0.50
            elif variance < 200:
                return 0.25
            else:
                return 0.12
        except:
            return 0.40
    
    def _improved_pitch(self, audio_array, sample_rate):
        """Pitch with micro-variations"""
        try:
            pitches, mags = librosa.piptrack(y=audio_array, sr=sample_rate)
            pitch_vals = []
            
            for t in range(pitches.shape[1]):
                idx = mags[:, t].argmax()
                if pitches[idx, t] > 0:
                    pitch_vals.append(pitches[idx, t])
            
            if len(pitch_vals) < 10:
                return 0.40
            
            mean = np.mean(pitch_vals)
            std = np.std(pitch_vals)
            cv = std / mean if mean > 0 else 0
            jitter = np.mean(np.abs(np.diff(pitch_vals)))
            
            # AI: stable + low jitter
            if cv < 0.05 and jitter < 3:
                return 0.75
            elif cv < 0.08 and jitter < 5:
                return 0.50
            elif cv < 0.12:
                return 0.25
            else:
                return 0.12
        except:
            return 0.40
    
    def _zcr(self, audio_array):
        """Zero-crossing rate"""
        try:
            zcr = librosa.feature.zero_crossing_rate(audio_array)
            zcr_std = np.std(zcr)
            
            if zcr_std < 0.015:
                return 0.70
            elif zcr_std < 0.030:
                return 0.40
            elif zcr_std < 0.050:
                return 0.18
            else:
                return 0.08
        except:
            return 0.40
    
    def _energy(self, audio_array):
        """Energy distribution"""
        try:
            rms = librosa.feature.rms(y=audio_array)[0]
            var = np.var(rms)
            
            if var < 0.00008:
                return 0.65
            elif var < 0.0003:
                return 0.35
            elif var < 0.0008:
                return 0.18
            else:
                return 0.08
        except:
            return 0.40


# Compatibility
EnhancedDeepfakeDetector = ImprovedDeepfakeDetector
DeepfakeDetector = ImprovedDeepfakeDetector
MLDeepfakeDetector = ImprovedDeepfakeDetector
