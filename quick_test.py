import requests

url = "https://honeypot-api-system.onrender.com/analyze"
headers = {
    "x-api-key": "honeypot_secret_2026",
    "Content-Type": "application/json"
}
payload = {
    "sessionId": "quick-test",
    "message": {
        "sender": "scammer",
        "text": "Your account blocked share OTP",
        "timestamp": "2026-01-26T10:00:00Z"
    },
    "conversationHistory": []
}

print("Testing deployed API...")
try:
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
