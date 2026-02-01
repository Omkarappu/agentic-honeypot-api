from typing import List, Dict
from config import config
import random

class AIAgent:
    def __init__(self):
        self.client = None
        try:
            from openai import OpenAI
            if config.OPENAI_API_KEY and config.OPENAI_API_KEY.strip():
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        except Exception as e:
            print(f"Warning: OpenAI not available: {e}")
    
    def generate_response(self, scammer_message: str, conversation_history: List[Dict]) -> str:
        if self.client:
            try:
                messages = [{"role": "system", "content": config.AGENT_SYSTEM_PROMPT}]
                
                for msg in conversation_history[-5:]:
                    if msg.get("sender") == "scammer":
                        messages.append({"role": "user", "content": msg.get("text", "")})
                    else:
                        messages.append({"role": "assistant", "content": msg.get("text", "")})
                
                messages.append({"role": "user", "content": scammer_message})
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=100,
                    temperature=0.8
                )
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error calling OpenAI: {e}")
                return self._fallback_response(scammer_message)
        else:
            return self._fallback_response(scammer_message)
    
    def _fallback_response(self, message: str) -> str:
        fallback_responses = [
            "I'm not sure about that. Can you explain more clearly?",
            "That sounds unusual. Why would you need my bank details?",
            "I'm confused. Could you tell me more about this offer?",
            "This seems suspicious. What exactly are you trying to do?",
            "I don't understand. Can you provide more information?",
            "That's interesting. How does this work exactly?",
            "I need to think about this. Give me more details.",
            "Why should I trust you with this information?"
        ]
        return random.choice(fallback_responses)

agent = AIAgent()
