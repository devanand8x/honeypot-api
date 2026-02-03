"""
Agentic Honey-Pot API
Main FastAPI application for GUVI Hackathon

Endpoints:
- POST /analyze - Analyze message and engage scammer
- GET /health - Health check
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from app.models import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    HealthResponse,
    EngagementMetrics,
    ExtractedIntelligence
)
from app.scam_detector import detect_scam, analyze_conversation_history
from app.agent import generate_response
from app.intelligence import extract_intelligence, merge_intelligence
from app.session import session_manager
from app.callback import send_guvi_callback, should_send_callback

# Load environment variables from .env file
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors for debugging but return standard FastAPI error format"""
    try:
        body = await request.body()
        body_str = body.decode()
    except Exception:
        body_str = "could not decode body"
    
    logger.error(f"Validation error: {exc.errors()}\nBody: {body_str}")
    # Return standard format to avoid confusing the automated tester
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Security: CORS Restricted Origins (Relaxed for evaluation stability)
ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security: Simple In-Memory Rate Limiter
from collections import defaultdict
import time
from fastapi import Request

# Store request timestamps: {ip: [timestamp1, timestamp2]}
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 200  # requests per window (increased for testing)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware"""
    client_ip = request.client.host
    now = time.time()
    
    # Clean up old timestamps
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] 
        if now - t < RATE_LIMIT_WINDOW
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(
            status_code=429, 
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    # Add new request
    rate_limit_store[client_ip].append(now)
    
    response = await call_next(request)
    return response

# Get API key from environment
API_KEY = os.getenv("API_KEY", "default_secret_key")


def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header"""
    # Re-read from env in case of hot reload issues
    expected_key = os.getenv("API_KEY", API_KEY)
    if x_api_key is None or x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return x_api_key


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze",
            "health": "GET /health"
        }
    }


@app.post("/", response_model=AnalyzeResponse)
async def analyze_message_root(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """Alias for /analyze to support base URL testing"""
    return await analyze_message(request, background_tasks, x_api_key)


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """
    Main endpoint to analyze incoming messages
    
    Flow:
    1. Verify API key
    2. Get/create session
    3. Detect scam intent
    4. If scam: activate AI agent
    5. Extract intelligence
    6. Return response
    7. Send GUVI callback if conditions met
    """
    
    # Verify API key
    verify_api_key(x_api_key)
    
    try:
        # Get or create session
        session = session_manager.get_or_create(request.sessionId)
        session_manager.update_activity(request.sessionId)
        session_manager.increment_message_count(request.sessionId)
        
        # Convert conversation history for processing
        history_dicts = [
            {"sender": msg.sender, "text": msg.text, "timestamp": msg.timestamp}
            for msg in request.conversationHistory
        ]
        
        # Detect scam in current message
        is_scam, confidence, keywords, notes = detect_scam(request.message.text)
        
        # Also analyze conversation history
        history_score, history_keywords = analyze_conversation_history(history_dicts)
        
        # Combine scam detection results
        final_scam = is_scam or history_score > 0.3 or session.scam_detected
        all_keywords = list(set(keywords + history_keywords))
        
        # Update session
        session_manager.set_scam_detected(request.sessionId, final_scam)
        
        # Extract intelligence from current message
        intelligence = extract_intelligence(request.message.text, session.intelligence)
        
        # Also extract from history
        for msg in history_dicts:
            if msg.get("sender") == "scammer":
                intelligence = extract_intelligence(msg.get("text", ""), intelligence)
        
        # Add detected keywords to intelligence
        intelligence.suspiciousKeywords = list(set(
            intelligence.suspiciousKeywords + all_keywords
        ))
        
        session_manager.update_intelligence(request.sessionId, intelligence)
        session_manager.update_notes(request.sessionId, notes)
        
        # Generate agent response if scam detected
        agent_response = None
        if final_scam:
            agent_response = generate_response(
                current_message=request.message.text,
                conversation_history=history_dicts,
                scam_type="general"
            )
            session_manager.set_last_response(request.sessionId, agent_response)
        
        # Get engagement metrics
        duration = session_manager.get_engagement_duration(request.sessionId)
        message_count = session.message_count
        
        # Check if callback should be sent
        if should_send_callback(
            scam_detected=final_scam,
            message_count=message_count,
            callback_already_sent=session.callback_sent
        ):
            # Send callback in background
            background_tasks.add_task(
                send_guvi_callback,
                session_id=request.sessionId,
                scam_detected=final_scam,
                total_messages=message_count,
                intelligence=intelligence,
                agent_notes=notes
            )
            session_manager.mark_callback_sent(request.sessionId)
        
        # Build response with STRICT intelligence (only 3 fields from Section 8)
        strict_intelligence = ExtractedIntelligence(
            bankAccounts=intelligence.bankAccounts,
            upiIds=intelligence.upiIds,
            phishingLinks=intelligence.phishingLinks
        )

        response = AnalyzeResponse(
            status="success",
            scamDetected=final_scam,
            agentResponse=agent_response,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=duration,
                totalMessagesExchanged=message_count
            ),
            extractedIntelligence=strict_intelligence,
            agentNotes=notes
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/session/{session_id}")
async def get_session(
    session_id: str,
    x_api_key: str = Header(None)
):
    """Get session details"""
    verify_api_key(x_api_key)
    
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "sessionId": session.session_id,
        "status": "active",
        "scamDetected": session.scam_detected,
        "messageCount": session.message_count,
        "startTime": session.start_time.isoformat(),
        "lastActivity": session.last_activity.isoformat(),
        "callbackSent": session.callback_sent,
        "extractedIntelligence": {
            "bankAccounts": session.intelligence.bankAccounts,
            "upiIds": session.intelligence.upiIds,
            "phoneNumbers": session.intelligence.phoneNumbers,
            "phishingLinks": session.intelligence.phishingLinks,
            "suspiciousKeywords": session.intelligence.suspiciousKeywords
        }
    }


@app.delete("/session/{session_id}")
async def end_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """End session and trigger callback"""
    verify_api_key(x_api_key)
    
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Send final callback if not already sent
    if session.scam_detected and not session.callback_sent:
        background_tasks.add_task(
            send_guvi_callback,
            session_id=session_id,
            scam_detected=session.scam_detected,
            total_messages=session.message_count,
            intelligence=session.intelligence,
            agent_notes=session.agent_notes
        )
        session_manager.mark_callback_sent(session_id)
    
    return {
        "status": "terminated",
        "callbackSent": True
    }


# Run with: uvicorn app.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
