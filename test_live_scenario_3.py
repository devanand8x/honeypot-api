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

def test_lottery_scam():
    session_id = f"lottery-test-{uuid.uuid4().hex[:8]}"
    print(f"\n🚀 Starting Lottery Scam Test | Session ID: {session_id}")
    print("-" * 50)

    # Turn 1: Prize Announcement + UPI Fee
    turn1_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "CONGRATULATIONS! You won 1 Crore in KBC Lottery. Pay 2500 Rs processing fee to upi-prize@oksbi",
            "timestamp": "2026-02-04T14:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "WhatsApp"}
    }

    print(f"Turn 1: Sending Prize Alert with UPI ID...")
    r1 = requests.post(f"{API_URL}/analyze", json=turn1_payload, headers=HEADERS)
    res1 = r1.json()
    print(f"Status: {r1.status_code}")
    print(f"Scam Detected: {res1.get('scamDetected')}")
    print(f"UPI Extracted: {res1.get('extractedIntelligence', {}).get('upiIds')}")

    time.sleep(2)

    # Turn 2: Identity Verification + Bank Account
    turn2_payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "To transfer the prize, send your bank account number and Aadhaar photo to +91 9988776655. Example: Ac 9182736450. Hurry!",
            "timestamp": "2026-02-04T14:05:00Z"
        },
        "conversationHistory": [
            turn1_payload["message"],
            {"sender": "user", "text": res1.get("agentResponse", "How do I claim my 1 crore?")}
        ],
        "metadata": {"channel": "WhatsApp"}
    }

    print(f"\nTurn 2: Sending Bank Account Context & Phone Number...")
    r2 = requests.post(f"{API_URL}/analyze", json=turn2_payload, headers=HEADERS)
    res2 = r2.json()
    print(f"Status: {r2.status_code}")
    print(f"Phone Extracted: {res2.get('extractedIntelligence', {}).get('phoneNumbers')}")
    print(f"Bank Account Extracted: {res2.get('extractedIntelligence', {}).get('bankAccounts')}")
    print(f"Total Messages: {res2.get('engagementMetrics', {}).get('totalMessagesExchanged')}")

    print("\n✅ Lottery Scam Test Completed!")

if __name__ == "__main__":
    test_lottery_scam()
