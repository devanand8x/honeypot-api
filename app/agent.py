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
from openai import AsyncOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

# Global clients
_client = None
_nvidia_client = None

def get_gemini_client():
    """Get or create Google Gemini client"""
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            api_key = api_key.strip()
            try:
                # Use the genai.Client with the vertexai-like interface
                # For async, we'll initialize it once
                _client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
    return _client


def get_nvidia_client():
    """Build and return NVIDIA client for fallback"""
    global _nvidia_client
    if _nvidia_client is None:
        api_key = os.getenv("NVIDIA_API_KEY")
        if api_key:
            api_key = api_key.strip()
            try:
                _nvidia_client = AsyncOpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=api_key
                )
                logger.info("NVIDIA Async client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize NVIDIA client: {e}")
                return None
    return _nvidia_client


def get_fallback_response(message: str) -> str:
    """Randomized fallback responses to keep Ramesh in character when LLM fails"""
    FALLBACKS = [
        "Sir please wait, let me ask my son. He handles all money matters.",
        "Bhaiya main thoda confuse ho gaya hoon. Ek baar phir se samjhayenge?",
        "Sir mera phone hang ho raha hai. Please ek minute rukiye... network issue hai.",
        "Oh ho! Account block ho jayega? Main abhi check karta hoon sir, tension ho rahi hai.",
        "Sir OTP nahi mil raha, main network thik karke batata hoon. Please wait.",
        "Sir which bank account? I have SBI and PNB both. Which one has problem?",
        "Sir I am very scared. Please tell me step by step what I need to do.",
        "Is this account safe sir? I am getting very worried about my money.",
        "I am not good with these apps sir. Can you explain how to tell my son?",
        "Sir the link you sent is not opening on my phone. Can you send again?"
    ]
    return random.choice(FALLBACKS)


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

async def generate_response(
    current_message: str,
    conversation_history: List[dict] = None,
    scam_type: str = "general"
) -> str:
    """
    Generate a human-like response using Asynchronous AI calls
    """
    
    if conversation_history is None:
        conversation_history = []
    
    conversation_context = build_conversation_context(
        conversation_history, 
        current_message
    )
    
    # Try NVIDIA first (Primary)
    nvidia_client = get_nvidia_client()
    if nvidia_client:
        # Try up to 2 times with different models if 503 occurs
        models_to_try = ["meta/llama-3.1-8b-instruct", "meta/llama3-8b-instruct"]
        for model_name in models_to_try:
            try:
                logger.info(f"Attempting Async NVIDIA response with {model_name}...")
                import asyncio
                response = await asyncio.wait_for(
                    nvidia_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, 
                                 {"role": "user", "content": f"CONVERSATION SO FAR:\n{conversation_context}\n\nGenerate your response as Ramesh."}],
                        temperature=0.7,
                        max_tokens=150,
                    ),
                    timeout=10.0 # 10 second limit per attempt
                )
                if response.choices[0].message.content:
                    logger.info(f"NVIDIA success with {model_name}")
                    return response.choices[0].message.content.strip()
            except asyncio.TimeoutError:
                logger.warning(f"NVIDIA {model_name} timed out.")
                continue
            except Exception as nv_e:
                # If it's a 503, try the next model
                if "503" in str(nv_e):
                    logger.warning(f"NVIDIA {model_name} 503'd, trying next...")
                    continue
                logger.warning(f"NVIDIA Async failed - Error Type: {type(nv_e).__name__}, Message: {str(nv_e)}")
                break # Non-503 error, move to Gemini

    # Fallback to Gemini
    client = get_gemini_client()
    if client:
        try:
            logger.info("Attempting Async Gemini (via ThreadPool fallback if necessary)...")
            import asyncio
            from functools import partial
            
            # The current genai SDK might not be fully async-native in all environments, 
            # so we run it in a thread to keep the loop free
            loop = asyncio.get_event_loop()
            full_prompt = f"{SYSTEM_PROMPT}\n\nCONVERSATION SO FAR:\n{conversation_context}\n\nGenerate your response as Ramesh."
            
            response = await asyncio.wait_for(
                loop.run_in_executor(None, partial(
                    client.models.generate_content,
                    model="gemini-2.0-flash",
                    contents=full_prompt
                )),
                timeout=10.0 # 10 second limit for secondary
            )
            
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini Async fallback error: {e}")

    return get_fallback_response(current_message)

