"""
Session Management Module
Handles multi-turn conversation state
"""

from typing import Dict, Optional
from datetime import datetime
import logging
from app.models import SessionIntelligence

logger = logging.getLogger(__name__)


import json
from pathlib import Path
from filelock import FileLock

DATA_FILE = Path(__file__).parent.parent / "sessions.json"
LOCK_FILE = Path(__file__).parent.parent / "sessions.json.lock"


class Session:
    """Represents a single conversation session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.message_count = 0
        self.scam_detected = False
        self.intelligence = SessionIntelligence()
        self.agent_notes = ""
        self.conversation_history = []
        self.last_agent_response = ""
        self.callback_sent = False

    def to_dict(self) -> dict:
        """Convert session to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "message_count": self.message_count,
            "scam_detected": self.scam_detected,
            "intelligence": self.intelligence.model_dump(),
            "agent_notes": self.agent_notes,
            "conversation_history": self.conversation_history,
            "last_agent_response": self.last_agent_response,
            "callback_sent": self.callback_sent
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create session from dictionary"""
        session = cls(data["session_id"])
        session.start_time = datetime.fromisoformat(data["start_time"])
        session.last_activity = datetime.fromisoformat(data["last_activity"])
        session.message_count = data["message_count"]
        session.scam_detected = data["scam_detected"]
        session.intelligence = SessionIntelligence.model_validate(data.get("intelligence", {}))
        session.agent_notes = data["agent_notes"]
        session.conversation_history = data["conversation_history"]
        session.last_agent_response = data["last_agent_response"]
        session.callback_sent = data["callback_sent"]
        return session


class SessionManager:
    """In-memory session storage with JSON persistence"""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self.load_from_disk()
    
    def load_from_disk(self) -> None:
        """Load sessions from JSON file with file locking"""
        if DATA_FILE.exists():
            try:
                with FileLock(LOCK_FILE):
                    with open(DATA_FILE, "r") as f:
                        data = json.load(f)
                        for session_data in data.values():
                            session = Session.from_dict(session_data)
                            self._sessions[session.session_id] = session
                logger.info(f"Loaded {len(self._sessions)} sessions from disk")
            except Exception as e:
                logger.error(f"Failed to load sessions: {e}")

    def save_to_disk(self) -> None:
        """Save sessions to JSON file with file locking"""
        try:
            with FileLock(LOCK_FILE):
                data = {sid: session.to_dict() for sid, session in self._sessions.items()}
                with open(DATA_FILE, "w") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")

    def get_or_create(self, session_id: str) -> Session:
        """Get existing session or create new one"""
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id)
            self.save_to_disk()
        return self._sessions[session_id]
    
    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self._sessions.get(session_id)
    
    def update_activity(self, session_id: str):
        """Update last activity timestamp"""
        if session_id in self._sessions:
            self._sessions[session_id].last_activity = datetime.now()
            self.save_to_disk()
    
    def increment_message_count(self, session_id: str):
        """Increment message count for session"""
        if session_id in self._sessions:
            self._sessions[session_id].message_count += 1
            self.save_to_disk()
    
    def set_scam_detected(self, session_id: str, detected: bool):
        """Mark session as scam detected"""
        if session_id in self._sessions:
            self._sessions[session_id].scam_detected = detected
            self.save_to_disk()
    
    def update_intelligence(self, session_id: str, intelligence: SessionIntelligence):
        """Update extracted intelligence"""
        if session_id in self._sessions:
            self._sessions[session_id].intelligence = intelligence
            self.save_to_disk()
    
    def update_notes(self, session_id: str, notes: str):
        """Update agent notes"""
        if session_id in self._sessions:
            self._sessions[session_id].agent_notes = notes
            self.save_to_disk()
    
    def set_last_response(self, session_id: str, response: str):
        """Store last agent response"""
        if session_id in self._sessions:
            self._sessions[session_id].last_agent_response = response
            self.save_to_disk()
    
    def mark_callback_sent(self, session_id: str):
        """Mark that callback was sent"""
        if session_id in self._sessions:
            self._sessions[session_id].callback_sent = True
            self.save_to_disk()
    
    def get_engagement_duration(self, session_id: str) -> int:
        """Get engagement duration in seconds"""
        session = self._sessions.get(session_id)
        if session:
            delta = session.last_activity - session.start_time
            return int(delta.total_seconds())
        return 0
    
    def delete(self, session_id: str):
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            self.save_to_disk()


# Global session manager instance
session_manager = SessionManager()
