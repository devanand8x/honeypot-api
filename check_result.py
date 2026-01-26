import requests
import json

url = "https://honeypot-api-system.onrender.com/analyze"
headers = {
    "x-api-key": "honeypot_secret_2026",
    "Content-Type": "application/json"
}
payload = {
    "sessionId": "final-verify-111",
    "message": {
        "sender": "scammer",
        "text": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
        "timestamp": "2026-01-26T10:00:00Z"
    },
    "conversationHistory": []
}

print("Testing exact scam message from screenshot...")
try:
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"Status: {r.status_code}")
    print("Response JSON:")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
