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