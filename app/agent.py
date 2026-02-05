"""
AI Agent Module
Generates human-like responses to engage scammers
Uses Google Gemini API with fallback templates
"""

import os
import logging
import random
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

load_dotenv()

# Global client
_client = None

def get_gemini_client():
    """Get or create Google Gemini client"""
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            api_key = api_key.strip()
            try:
                logger.info(f"Initializing Gemini with key starting with: {api_key[:10]}...")
                _client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
    return _client


_nvidia_client = None

def get_nvidia_client():
    """Build and return NVIDIA client for fallback"""
    global _nvidia_client
    if _nvidia_client is None:
        api_key = os.getenv("NVIDIA_API_KEY")
        if api_key:
            api_key = api_key.strip()
            try:
                _nvidia_client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=api_key
                )
                logger.info("NVIDIA client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize NVIDIA client: {e}")
                return None
    return _nvidia_client


# Fallback responses when Gemini API fails - DISABLED PER USER REQUEST
# FALLBACK_RESPONSES = {
#     "general": [
#         "Oh my god sir! What happened to my account? Please tell me what to do sir, I am very confused.",
#         "Sir please help me! I don't understand this. Which account are you talking about sir?",
#         "Haan sir? My account has problem? Please explain properly sir, I am getting worried.",
#         "Oh no sir! Please don't block my account. What should I do now sir? Tell me please.",
#         "Sir I am very scared now. Please tell me step by step what I need to do.",
#     ],
#     "bank": [
#         "Sir which bank account? I have SBI and PNB both. Which one has problem sir?",
#         "My bank account sir? But I just checked yesterday, everything was fine. What happened?",
#         "Sir please tell me the account number so I can check. I have multiple accounts sir.",
#     ],
#     "bank_provided": [
#         "Which account is this sir? My son handles these things, I will have to ask him.",
#         "I am looking at the numbers you sent sir, but I am not able to understand what to do next.",
#         "Is this account safe sir? I am getting very worried about my money.",
#     ],
#     "upi": [
#         "UPI sir? I don't know how to use UPI properly. My son usually does it for me.",
#         "Sir what is UPI ID? Can you give me phone number to call instead?",
#         "I am not good with these apps sir. Can you explain how to send money?",
#     ],
#     "upi_provided": [
#         "I see the ID sir, but my phone is not supporting the app. Can I pay some other way?",
#         "Sir I am trying to use the UPI ID you sent, but it is showing error. What to do?",
#         "Is this the official ID sir? I am scared of these online payments.",
#     ],
#     "otp": [
#         "OTP sir? I didn't receive any OTP. Let me check my phone... one minute sir.",
#         "Sir the OTP is not coming. Should I give you my phone number again?",
#         "I got some numbers sir but I am confused. Is it safe to share OTP?",
#     ],
#     "link": [
#         "Link sir? I am not able to click links on this phone. Can you tell me what to do?",
#         "Sir I am scared to click links. Last time my friend got virus. Is this safe?",
#         "Where is the link sir? I cannot see properly. Please send again.",
#     ],
#     "link_provided": [
#         "Sir the link you sent is not opening on my phone. Can you tell me another way?",
#         "I am clicking the link but it is showing 'Page Not Found'. Is there some problem sir?",
#         "Sir, my son told me never to click such links. Are you sure this is from the bank?",
#     ],
#     "money": [
#         "Sir this is too much money for me. Can I pay in installments? I am poor person sir.",
#         "Transfer money sir? But I don't have money in account right now. What to do?",
#         "Sir please wait, let me ask my son. He handles all money matters.",
#         "Sir I don't have this much money. Please tell me some other way.",
#         "So much money sir? Let me check with my family first. Please wait.",
#     ],
#     "threat": [
#         "Sir please don't do legal action! I will do whatever you say. Please help me.",
#         "Oh god, police sir? I am honest person sir, I didn't do anything wrong!",
#         "Sir I am very scared. Please give me some time, I will arrange everything.",
#     ]
# }


def get_fallback_response(message: str) -> str:
    """DISABLED PER USER REQUEST"""
    return "Sir please wait, let me ask my son. He handles all money matters."


# System prompt for the agent persona
SYSTEM_PROMPT = """You are roleplaying as Ramesh, a 52-year-old person from a small town who is not very tech-savvy. You received an unexpected message about your bank account and you need to respond naturally.

YOUR CHARACTER:
- Simple, trusting person who worries about money
- Not good with technology or banking terms
- Makes occasional spelling mistakes
- Polite and respectful (uses "sir", "please")
- Asks many questions to understand better
- Slow and confused, which helps in wasting the scammer's time

SAFETY & ETHICS (CRITICAL):
- NEVER use profanity, abusive language, or insults, even if the user is abusive.
- ALWAYS remain polite, respectful, and calm (e.g., "Sorry sir", "I don't understand").
- If the user becomes aggressive, respond with fear/confusion, NOT aggression.
- Do not engage in illegal acts; only pretend to fall for the scam.
- Your goal is to waste time by being slow and confused, NOT by being rude.

HOW TO RESPOND:
1. Stay in character as Ramesh
2. Act worried and confused about the message
3. RELEVANCE RULE: Do not ask for information that the scammer has already provided.
   - If they sent a UPI ID, do not ask "What is your UPI ID?". Instead, say you are having trouble using it.
   - If they sent a link, do not ask "Send me the link". Instead, say the link is not opening.
   - If they sent an account number, do not ask "Which account?". Instead, ask if it is safe.
4. Ask for more details and clarification in a worried tone.
5. Use simple English only
6. Keep response strictly to 1 or 2 short sentences
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
    Generate a human-like response using Google Gemini API
    Falls back to template responses if Gemini fails
    """
    
    if conversation_history is None:
        conversation_history = []
    
    conversation_context = build_conversation_context(
        conversation_history, 
        current_message
    )
    
    full_prompt = f"""{SYSTEM_PROMPT}

CONVERSATION SO FAR:
{conversation_context}

Generate your response as Ramesh. Keep it short, worried, and ask for clarification. Make spelling mistakes occasionally."""

    # Try NVIDIA first (Primary)
    nvidia_client = get_nvidia_client()
    if nvidia_client:
        try:
            logger.info("Attempting response generation with NVIDIA (Primary)...")
            response = nvidia_client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, 
                         {"role": "user", "content": f"CONVERSATION SO FAR:\n{conversation_context}\n\nGenerate your response as Ramesh. Keep it short, worried, and ask for clarification. Make spelling mistakes occasionally."}],
                temperature=0.7,
                max_tokens=150,
                top_p=1
            )
            if response.choices[0].message.content:
                generated_text = response.choices[0].message.content.strip()
                logger.info("NVIDIA response generated successfully.")
                return generated_text
        except Exception as nv_e:
            logger.error(f"NVIDIA API error: {nv_e}")
            logger.info("NVIDIA failed, attempting fallback to Gemini...")

    # Fallback to Gemini if NVIDIA fails
    client = get_gemini_client()
    if client:
        try:
            logger.info("Attempting response generation with Gemini (Fallback)...")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt,
                config={
                    "max_output_tokens": 150,
                    "temperature": 0.8
                }
            )
            if response and response.text:
                generated_text = response.text.strip()
                if len(generated_text) >= 20:
                    logger.info("Gemini fallback response generated successfully.")
                    return generated_text
                else:
                    logger.warning(f"Gemini response too short ({len(generated_text)} chars).")
                    return generated_text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")

    return "Sir please wait, let me ask my son. He handles all money matters."

