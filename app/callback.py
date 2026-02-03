"""
GUVI Callback Module
Sends final results to GUVI evaluation endpoint
"""

import os
import httpx
import logging
from typing import Optional
from app.models import ExtractedIntelligence
from app.intelligence import intelligence_to_dict

logger = logging.getLogger(__name__)


GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


async def send_guvi_callback(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: str
) -> tuple[bool, Optional[str]]:
    """
    Send final result to GUVI evaluation endpoint
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    
    callback_url = os.getenv("GUVI_CALLBACK_URL", GUVI_CALLBACK_URL)
    
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence_to_dict(intelligence),
        "agentNotes": agent_notes
    }
    
    # Retry logic - 3 attempts with increasing timeout
    for attempt in range(3):
        try:
            timeout = 5 + (attempt * 2)  # 5s, 7s, 9s
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    callback_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"GUVI callback successful for session {session_id}")
                    return True, None
                else:
                    error_msg = f"GUVI callback failed: {response.status_code} - {response.text}"
                    logger.warning(error_msg)
                    
        except httpx.TimeoutException:
            logger.warning(f"GUVI callback timeout (attempt {attempt + 1}/3)")
            continue
        except Exception as e:
            logger.error(f"GUVI callback error: {e}")
            continue
    
    return False, "Failed after 3 attempts"


def should_send_callback(
    scam_detected: bool,
    message_count: int,
    callback_already_sent: bool
) -> bool:
    """
    Determine if callback should be sent
    
    Conditions:
    1. Scam was detected
    2. At least 1 message processed
    3. Callback not already sent for this session
    """
    
    if callback_already_sent:
        return False
    
    if not scam_detected:
        return False
    
    # Send callback immediately when scam is detected (changed from 3 to 1)
    if message_count >= 1:
        return True
    
    return False
