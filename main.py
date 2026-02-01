from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import requests

from config import config
from scam_detector import scam_detector
from extractor import extractor
from agent import agent

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="Scam Detection & Intelligence Extraction - GUVI Hackathon",
    version="1.0.0"
)

class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class MetaData(BaseModel):
    channel: str = "SMS"
    language: str = "English"
    locale: str = "IN"

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict] = []
    metadata: Optional[MetaData] = None

class HoneypotResponse(BaseModel):
    status: str
    reply: str
    scamDetected: Optional[bool] = None
    confidence: Optional[float] = None

sessions = {}

@app.get("/")
async def health():
    return {"status": "online", "message": "Agentic Honey-Pot API is running"}

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(request: HoneypotRequest, x_api_key: str = Header(None)):
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    session_id = request.sessionId
    message_text = request.message.text
    sender = request.message.sender
    
    if session_id not in sessions:
        sessions[session_id] = {"messages": [], "scam_detected": False, "confidence": 0.0, "turn_count": 0, "status": "active"}
    
    session = sessions[session_id]
    
    if session["status"] == "finalized":
        raise HTTPException(status_code=400, detail="Session already finalized")
    
    session["messages"].append({"sender": sender, "text": message_text, "timestamp": request.message.timestamp})
    session["turn_count"] += 1
    
    is_scam, confidence = scam_detector.detect_scam(message_text)
    
    if is_scam and not session["scam_detected"]:
        session["scam_detected"] = True
        session["confidence"] = confidence
    
    agent_response = agent.generate_response(message_text, session["messages"])
    
    session["messages"].append({"sender": "user", "text": agent_response, "timestamp": datetime.utcnow().isoformat() + "Z"})
    
    if session["scam_detected"] and session["turn_count"] >= config.MIN_ENGAGEMENT_TURNS:
        finalize_session(session_id)
    
    return HoneypotResponse(status="success", reply=agent_response, scamDetected=session["scam_detected"], confidence=session["confidence"])

@app.post("/api/honeypot/finalize")
async def finalize_endpoint(sessionId: str, x_api_key: str = Header(None)):
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return finalize_session(sessionId)

@app.get("/api/honeypot/session/{sessionId}")
async def get_session(sessionId: str, x_api_key: str = Header(None)):
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if sessionId not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[sessionId]

def finalize_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session["status"] == "finalized":
        return {"status": "already_finalized", "sessionId": session_id}
    
    conversation_text = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in session["messages"]])
    intelligence = extractor.extract_intelligence(conversation_text)
    
    payload = {
        "sessionId": session_id,
        "scamDetected": session["scam_detected"],
        "totalMessagesExchanged": session["turn_count"],
        "extractedIntelligence": {
            "bankAccounts": intelligence["bankAccounts"],
            "upiIds": intelligence["upiIds"],
            "phishingLinks": intelligence["phishingLinks"],
            "phoneNumbers": intelligence["phoneNumbers"],
            "suspiciousKeywords": intelligence["suspiciousKeywords"]
        },
        "agentNotes": f"Session lasted {session['turn_count']} turns. Scam confidence: {session['confidence']:.2f}"
    }
    
    try:
        response = requests.post(config.GUVI_CALLBACK_URL, json=payload, headers={"x-api-key": config.API_KEY}, timeout=10)
        if response.status_code in [200, 201]:
            session["status"] = "finalized"
            return {"status": "success", "sessionId": session_id, "message": "Results sent to GUVI", "payload": payload}
        else:
            return {"status": "error", "sessionId": session_id, "message": f"GUVI callback returned {response.status_code}"}
    except Exception as e:
        return {"status": "error", "sessionId": session_id, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
