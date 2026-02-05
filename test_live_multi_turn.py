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

def test_session():
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    print(f"\n🚀 Starting Multi-Turn Test | Session ID: {session_id}")
    print("-" * 50)

    # Turn 1: Initial Scam Message
    turn1_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "URGENT: Your SBI account is compromised. Call 9876543210 immediately to verify.",
            "timestamp": "2026-02-04T12:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS"}
    }

    print(f"Turn 1: Sending suspicious message with Phone Number...")
    r1 = requests.post(f"{API_URL}/analyze", json=turn1_payload, headers=HEADERS)
    print(f"Status: {r1.status_code}")
    res1 = r1.json()
    print(f"Scam Detected: {res1.get('scamDetected')}")
    print(f"Agent Response: {res1.get('agentResponse')}")
    print(f"Phone Numbers Extracted: {res1.get('extractedIntelligence', {}).get('phoneNumbers')}")

    time.sleep(2) # Natural delay

    # Turn 2: Follow-up with UPI
    turn2_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Send 1000 Rs to test-scammer@ybl to unblock your account.",
            "timestamp": "2026-02-04T12:02:00Z"
        },
        "conversationHistory": [
            turn1_payload["message"],
            {"sender": "user", "text": res1.get("agentResponse", "Hello, who is this?")}
        ],
        "metadata": {"channel": "SMS"}
    }

    print(f"\nTurn 2: Sending message with UPI ID...")
    r2 = requests.post(f"{API_URL}/analyze", json=turn2_payload, headers=HEADERS)
    res2 = r2.json()
    print(f"Status: {r2.status_code}")
    print(f"UPI Extracted: {res2.get('extractedIntelligence', {}).get('upiIds')}")
    print(f"Total Messages: {res2.get('engagementMetrics', {}).get('totalMessagesExchanged')}")

    print("\n✅ Multi-Turn Test Completed!")

if __name__ == "__main__":
    test_session()
