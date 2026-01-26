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
    sessionId: str
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
    PS Section 8 - extractedIntelligence object
    NOTE: Section 8 only has bankAccounts, upiIds, phishingLinks
    Section 12 callback adds phoneNumbers, suspiciousKeywords
    """
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    # Added for Section 12 callback compatibility:
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []


class AnalyzeResponse(BaseModel):
    """
    PS Section 8 - Response body EXACT
    
    {
        "status": "success",
        "scamDetected": true,
        "engagementMetrics": {
            "engagementDurationSeconds": 420,
            "totalMessagesExchanged": 18
        },
        "extractedIntelligence": {
            "bankAccounts": ["XXXX-XXXX-XXXX"],
            "upiIds": ["scammer@upi"],
            "phishingLinks": ["http://malicious-link.example"]
        },
        "agentNotes": "Scammer used urgency tactics..."
    }
    """
    status: str = "success"
    scamDetected: bool = False
    engagementMetrics: EngagementMetrics = EngagementMetrics()
    extractedIntelligence: ExtractedIntelligence = ExtractedIntelligence()
    agentNotes: str = ""
    # agentResponse is needed for conversation but not in PS Section 8
    # Adding at end to not break PS format appearance
    agentResponse: Optional[str] = None


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
