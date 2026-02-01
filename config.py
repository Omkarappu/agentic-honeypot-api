import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("API_KEY", "honeypot-secret-key-guvi-2026")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    SCAM_CONFIDENCE_THRESHOLD = 0.5
    MIN_ENGAGEMENT_TURNS = 2
    MAX_ENGAGEMENT_TURNS = 20
    AGENT_SYSTEM_PROMPT = """You are an ordinary person who received a suspicious message about banking or money. 
You don't suspect fraud yet, but you're cautious. Respond naturally and briefly (1-2 sentences).
Ask questions to understand better. Keep conversation going. Act like a real human."""

config = Config()
