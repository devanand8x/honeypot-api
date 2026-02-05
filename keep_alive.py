import requests
import time
from datetime import datetime

# The health endpoint of our deployed API
URL = "https://honeypot-api-system.onrender.com/health"

def keep_alive():
    print("🚀 binary_geeks Robust Keep-Alive Script is Running!")
    print(f"Target: {URL}")
    print("Pinging root (/) and /health every 60 seconds...")
    print("-" * 50)

    endpoints = [URL, URL.replace("/health", "/")]

    while True:
        for target in endpoints:
            try:
                # Increased timeout to 20s to handle slow 'spin-ups'
                response = requests.get(target, timeout=20)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                if response.status_code == 200:
                    print(f"[{timestamp}] ✅ Success: {target.split('/')[-1] if target.endswith('health') else 'root'}")
                else:
                    print(f"[{timestamp}] ⚠️ Status {response.status_code}: {target}")
                    
            except requests.exceptions.RequestException as e:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ❌ Timeout/Error for {target}")

        # Wait for 60 seconds before the next round of pings
        time.sleep(60)

if __name__ == "__main__":
    try:
        keep_alive()
    except KeyboardInterrupt:
        print("\n👋 Keep-Alive script stopped by user. API might sleep if idle.")
