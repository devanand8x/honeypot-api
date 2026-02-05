import requests
import json
import uuid
import time

# Configuration
API_URL = "https://honeypot-api-system.onrender.com"
API_KEY = "honeypot_secret_2026"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def test_social_engineering():
    session_id = f"social-test-{uuid.uuid4().hex[:8]}"
    print(f"\n🚀 Starting Social Engineering Test | Session ID: {session_id}")
    print("-" * 50)

    # Turn 1: Account Lock Urgency
    turn1_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Hey friend, I accidentally sent my 6-digit WhatsApp restoration code to you by mistake. Can you please send it back to me urgently?",
            "timestamp": "2026-02-04T15:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "WhatsApp"}
    }

    print(f"Turn 1: Sending restoration code request...")
    r1 = requests.post(f"{API_URL}/analyze", json=turn1_payload, headers=HEADERS)
    res1 = r1.json()
    print(f"Status: {r1.status_code}")
    print(f"Scam Detected: {res1.get('scamDetected')}")
    print(f"Keywords Found: {res1.get('extractedIntelligence', {}).get('suspiciousKeywords')}")

    time.sleep(2)

    # Turn 2: Direct Code Request
    turn2_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "The code is 251934. Just tell me if you got it. Also, confirm your number ends in 8899?",
            "timestamp": "2026-02-04T15:05:00Z"
        },
        "conversationHistory": [
            turn1_payload["message"],
            {"sender": "user", "text": res1.get("agentResponse", "Wait, I didn't get any code yet.")}
        ],
        "metadata": {"channel": "WhatsApp"}
    }

    print(f"\nTurn 2: Sending the numeric code (251934)...")
    r2 = requests.post(f"{API_URL}/analyze", json=turn2_payload, headers=HEADERS)
    res2 = r2.json()
    print(f"Status: {r2.status_code}")
    # Note: 6-digit codes might be extracted as 'bankAccount' or 'phone' keywords depending on length
    # But mostly they should be in agentNotes or suspiciousKeywords
    print(f"Detection Results: {res2.get('scamDetected')}")
    print(f"Agent Notes: {res2.get('agentNotes')}")
    print(f"Total Messages: {res2.get('engagementMetrics', {}).get('totalMessagesExchanged')}")

    print("\n✅ Social Engineering Test Completed!")

if __name__ == "__main__":
    test_social_engineering()
