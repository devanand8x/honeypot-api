import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load env
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

# Configuration
URL = "https://honeypot-api-system.onrender.com/" # Testing the live root flexible endpoint
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

TEST_PAYLOAD = {
    "message": "URGENT: Your bank account 1234 5678 9012 is blocked. To unblock, pay 5000 to upi@ybl immediately or visit http://scam-link.com",
    "sessionId": "test-session-final-ref",
    "conversationHistory": []
}

def run_test():
    print(f"🚀 Running Final API Verification Test...")
    print(f"Target URL: {URL}")
    print("-" * 50)
    
    try:
        response = requests.post(URL, json=TEST_PAYLOAD, headers=HEADERS, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print("Response Headers (X-Honeypot-Version):", response.headers.get("X-Honeypot-Version"))
        print("-" * 50)
        
        if response.status_code == 200:
            data = response.json()
            print("📦 API RESPONSE:")
            print(json.dumps(data, indent=4))
            
            # Validation
            print("-" * 50)
            print("✅ COMPLIANCE CHECK:")
            required_fields = ["status", "reply", "sessionId", "scamDetected", "agentResponse", "engagementMetrics", "extractedIntelligence", "agentNotes"]
            
            # Check field presence and order
            actual_keys = list(data.keys())
            for i, field in enumerate(required_fields):
                if field in data:
                    print(f"  [OK] '{field}' is present.")
                else:
                    print(f"  [FAIL] '{field}' is MISSING!")
            
            # Check intelligence extraction
            intel = data.get("extractedIntelligence", {})
            if "123456789012" in intel.get("bankAccounts", []):
                print("  [OK] Bank account extracted correctly.")
            if "upi@ybl" in intel.get("upiIds", []):
                print("  [OK] UPI ID extracted correctly.")
            if any("scam-link.com" in link for link in intel.get("phishingLinks", [])):
                print("  [OK] Phishing link extracted correctly.")
                
            print("-" * 50)
            print("🎉 Test Successful!")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test Failed with exception: {e}")

if __name__ == "__main__":
    run_test()
