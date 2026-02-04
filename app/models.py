"""
Pydantic models for request/response schemas
100% EXACT MATCH with GUVI Problem Statement
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime


# ============== REQUEST MODELS (PS Section 6) ==============

class Message(BaseModel):
    """
    PS Section 6.3 - message object
    """
    model_config = {"extra": "allow"}  # Allow extra fields
    
    sender: str = "scammer"  # "scammer" or "user"
    text: str = ""  # Message content
    timestamp: Optional[Union[str, int, float]] = Field(default_factory=lambda: datetime.now().isoformat())  # ISO-8601 or Unix timestamp


class Metadata(BaseModel):
    """
    PS Section 6.3 - metadata object (Optional)
    """
    channel: Optional[str] = "SMS"  # SMS/WhatsApp/Email/Chat
    language: Optional[str] = "English"  # Language used
    locale: Optional[str] = "IN"  # Country or region


class AnalyzeRequest(BaseModel):
    """
    PS Section 6.1 and 6.2 - Request body EXACT
    """
    model_config = {"extra": "allow"}  # Allow extra fields for flexibility
    
    sessionId: Optional[str] = Field(default_factory=lambda: f"session-{datetime.now().timestamp()}")
    message: Message
    conversationHistory: Optional[List[Message]] = []
    metadata: Optional[Metadata] = None


# ============== RESPONSE MODELS (PS Section 8 EXACT) ==============

class EngagementMetrics(BaseModel):
    """
    PS Section 8 - engagementMetrics object
    """
    engagementDurationSeconds: int = 0
    totalMessagesExchanged: int = 0


class ExtractedIntelligence(BaseModel):
    """
    Unified intelligence object covering both Section 8 and Section 12.
    """
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []


class SessionIntelligence(ExtractedIntelligence):
    """Internal storage (same as above for now)"""
    pass


class AnalyzeResponse(BaseModel):
    """
    PS Section 8 - Response body (Restored agentResponse as it is logically required)
    Added sessionId for better traceability as per Section 12.
    """
    status: str = "success"
    sessionId: str = ""
    scamDetected: bool = False
    agentResponse: Optional[str] = None
    engagementMetrics: EngagementMetrics = EngagementMetrics()
    extractedIntelligence: ExtractedIntelligence = ExtractedIntelligence()
    agentNotes: str = ""


# ============== CALLBACK MODEL (PS Section 12 EXACT) ==============

class CallbackPayload(BaseModel):
    """
    PS Section 12 - Callback payload EXACT
    
    {
        "sessionId": "abc123-session-id",
        "scamDetected": true,
        "totalMessagesExchanged": 18,
        "extractedIntelligence": {
            "bankAccounts": ["XXXX-XXXX-XXXX"],
            "upiIds": ["scammer@upi"],
            "phishingLinks": ["http://malicious-link.example"],
            "phoneNumbers": ["+91XXXXXXXXXX"],
            "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
        },
        "agentNotes": "Scammer used urgency tactics..."
    }
    """
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: dict
    agentNotes: str


# ============== UTILITY MODELS ==============

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
