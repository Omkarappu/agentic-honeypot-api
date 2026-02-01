import re
from typing import Dict, List

class IntelligenceExtractor:
    def extract_intelligence(self, text: str) -> Dict:
        return {
            "bankAccounts": self._extract_accounts(text),
            "upiIds": self._extract_upi(text),
            "phishingLinks": self._extract_links(text),
            "phoneNumbers": self._extract_phones(text),
            "suspiciousKeywords": self._extract_keywords(text)
        }
    
    def _extract_accounts(self, text: str) -> List[str]:
        matches = re.findall(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}(?:[-\s]?\d{4})?', text)
        return list(set(matches))
    
    def _extract_upi(self, text: str) -> List[str]:
        matches = re.findall(r'[\w\.-]+@(?:upi|okaxis|okhdfcbank|okicici|okpnb)', text, re.IGNORECASE)
        return list(set([m.lower() for m in matches]))
    
    def _extract_links(self, text: str) -> List[str]:
        matches = re.findall(r'https?://[^\s]+', text)
        return list(set(matches))
    
    def _extract_phones(self, text: str) -> List[str]:
        matches = re.findall(r'\+?91[-.\s]?\d{10}|\+\d{1,3}\d{9,}', text)
        return list(set(matches))
    
    def _extract_keywords(self, text: str) -> List[str]:
        keywords = ["urgent", "verify", "confirm", "blocked", "suspended", "update", "download", "install", "claim", "reward", "authenticate"]
        found = [kw for kw in keywords if kw in text.lower()]
        return list(set(found))

extractor = IntelligenceExtractor()
