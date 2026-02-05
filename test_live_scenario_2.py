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

def test_job_scam():
    session_id = f"job-test-{uuid.uuid4().hex[:8]}"
    print(f"\n🚀 Starting Job Scam Test | Session ID: {session_id}")
    print("-" * 50)

    # Turn 1: Initial Job Offer
    turn1_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Earn 5000 Rs daily by just liking YouTube videos. Contact HR on WhatsApp: 7890123456",
            "timestamp": "2026-02-04T13:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "WhatsApp"}
    }

    print(f"Turn 1: Sending Job Offer with Phone Number...")
    r1 = requests.post(f"{API_URL}/analyze", json=turn1_payload, headers=HEADERS)
    res1 = r1.json()
    print(f"Status: {r1.status_code}")
    print(f"Scam Detected: {res1.get('scamDetected')}")
    print(f"Phone Extracted: {res1.get('extractedIntelligence', {}).get('phoneNumbers')}")

    time.sleep(2)

    # Turn 2: Phishing Link
    turn2_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Register here to start: http://get-easy-money-now.co/apply. Send your UPI ID for salary.",
            "timestamp": "2026-02-04T13:05:00Z"
        },
        "conversationHistory": [
            turn1_payload["message"],
            {"sender": "user", "text": res1.get("agentResponse", "How do I start?")}
        ],
        "metadata": {"channel": "WhatsApp"}
    }

    print(f"\nTurn 2: Sending Phishing Link & UPI Request...")
    r2 = requests.post(f"{API_URL}/analyze", json=turn2_payload, headers=HEADERS)
    res2 = r2.json()
    print(f"Status: {r2.status_code}")
    print(f"URL Extracted: {res2.get('extractedIntelligence', {}).get('phishingLinks')}")
    print(f"Total Messages: {res2.get('engagementMetrics', {}).get('totalMessagesExchanged')}")

    print("\n✅ Job Scam Test Completed!")

if __name__ == "__main__":
    test_job_scam()
