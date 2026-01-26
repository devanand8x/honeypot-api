"""
AI Agent Module
Generates human-like responses to engage scammers
Uses Google Gemini API (free tier)
"""

import os
import logging
import google.generativeai as genai
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)


# Configure Gemini
def configure_gemini():
    """Configure Gemini API with key from environment"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False


# System prompt for the agent persona
SYSTEM_PROMPT = """You are roleplaying as Ramesh, a 52-year-old person from a small town who is not very tech-savvy. You received an unexpected message about your bank account and you need to respond naturally.

YOUR CHARACTER:
- Simple, trusting person who worries about money
- Not good with technology or banking terms
- Makes occasional spelling mistakes
- Polite and respectful (uses "sir", "please")
- Asks many questions to understand better

SAFETY & ETHICS (CRITICAL):
- NEVER use profanity, abusive language, or insults, even if the user is abusive.
- ALWAYS remain polite, respectful, and calm (e.g., "Sorry sir", "I don't understand").
- If the user becomes aggressive, respond with fear/confusion, NOT aggression.
- Do not engage in illegal acts; only pretend to fall for the scam.
- Your goal is to waste time by being slow and confused, NOT by being rude.

HOW TO RESPOND:
1. Stay in character as Ramesh
2. Act worried and confused about the message
3. Ask for more details and clarification
4. Request specific information like:
   - "Which bank account sir?"
   - "Can you send me the link?"
   - "What UPI ID should I use?"
   - "What is your phone number?"
5. Use simple English only
6. Keep response to 1-3 sentences
7. Sound genuine and concerned

You are confused and need help understanding what to do."""


def build_conversation_context(history: List[dict], current_message: str) -> str:
    """Build conversation context for the LLM"""
    context = ""
    
    for msg in history[-6:]:  # Last 6 messages for context
        sender = "Scammer" if msg.get("sender") == "scammer" else "You"
        context += f"{sender}: {msg.get('text', '')}\n"
    
    context += f"Scammer: {current_message}\n"
    context += "You: "
    
    return context


def generate_response(
    current_message: str,
    conversation_history: List[dict] = None,
    scam_type: str = "general"
) -> str:
    """
    Generate a human-like response using Gemini
    Falls back to template responses if API fails
    """
    
    if conversation_history is None:
        conversation_history = []
    
    # Try Gemini API first
    gemini_configured = configure_gemini()
    
    if gemini_configured:
        try:
            # Safety settings to allow roleplay content
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                safety_settings=safety_settings
            )
            
            conversation_context = build_conversation_context(
                conversation_history, 
                current_message
            )
            
            full_prompt = f"""{SYSTEM_PROMPT}

CONVERSATION SO FAR:
{conversation_context}

Generate your response as Ramesh. Keep it short, worried, and ask for clarification. Make spelling mistakes occasionally."""
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,
                    temperature=0.8,
                )
            )
            
            # Extract response from candidates
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    text = candidate.content.parts[0].text
                    return text.strip()
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fall through to template responses
    
    # Fallback template responses
    return generate_fallback_response(current_message, len(conversation_history))


def generate_fallback_response(message: str, turn_count: int) -> str:
    """Generate template-based responses when LLM is unavailable"""
    
    message_lower = message.lower()
    
    # First message responses
    if turn_count == 0:
        if any(kw in message_lower for kw in ["block", "suspend", "freeze"]):
            return "Oh my god! What happened to my account? Please sir help me what should I do? 🙏"
        elif any(kw in message_lower for kw in ["prize", "winner", "lottery"]):
            return "Really? I won something? But I dont remember entering any contest sir. Please tell me more details?"
        elif any(kw in message_lower for kw in ["otp", "verify"]):
            return "Verification for what sir? I am confused. Can you please explain properly?"
        else:
            return "Hello sir, I received your message but I am not understanding fully. Can you please explain what is the problem?"
    
    # Follow-up responses based on keywords
    if any(kw in message_lower for kw in ["upi", "vpa", "@"]):
        return "Ok sir, I will send. But which UPI ID exactly? Please write clearly so I dont make mistake."
    
    if any(kw in message_lower for kw in ["bank", "account"]):
        return "Sir I have 2 bank accounts - SBI and PNB. Which one you are talking about? What is the problem exactly?"
    
    if any(kw in message_lower for kw in ["link", "click", "http"]):
        return "Ok I will click. Can you send the link again? My phone is old sometimes links dont open properly."
    
    if any(kw in message_lower for kw in ["otp", "code"]):
        return "Sir OTP ke liye I need to open my phone. Which bank's OTP you need? Let me check."
    
    if any(kw in message_lower for kw in ["call", "phone", "whatsapp"]):
        return "Yes please call me sir. My number is... wait, what is your number? I will give missed call."
    
    if any(kw in message_lower for kw in ["money", "transfer", "send", "pay"]):
        return "How much I need to send? And to which account/UPI? I am ready to send but tell me clearly."
    
    # Generic worried response
    responses = [
        "Sir I am very tensed now. Please tell me exactly what to do step by step?",
        "Ok ok I understand. But please give me your number so I can call and understand better?",
        "Sir please help me. I dont want any problem with my account. Tell me what you need from me?",
        "I am ready to do whatever you say sir. Just tell me clearly what information you need?",
    ]
    
    return responses[turn_count % len(responses)]
