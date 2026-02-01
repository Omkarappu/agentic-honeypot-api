import re
from typing import Dict, List, Tuple

class ScamDetector:
    SCAM_KEYWORDS = {
        "urgency": ["urgent", "immediately", "right now", "asap", "now", "quickly"],
        "account_threats": ["blocked", "suspended", "locked", "closed", "verification required", "confirm"],
        "financial": ["send payment", "transfer", "account details", "card details", "otp", "upi"],
        "prizes": ["congratulations", "won", "reward", "prize", "claim"],
        "links": ["click here", "verify link", "download", "update app", "install"]
    }
    
    def detect_scam(self, message: str) -> Tuple[bool, float]:
        message_lower = message.lower()
        score = 0.0
        
        for category, keywords in self.SCAM_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            if matches > 0:
                score += matches * 0.15
        
        if re.search(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}', message):
            score += 0.2
        if re.search(r'[\w\.-]+@upi', message, re.IGNORECASE):
            score += 0.2
        if re.search(r'http[s]?://[^\s]+', message):
            score += 0.1
        if re.search(r'\+?91[-.\s]?\d{10}', message):
            score += 0.1
        
        confidence = min(1.0, score)
        is_scam = confidence >= 0.5
        
        return is_scam, confidence

scam_detector = ScamDetector()
