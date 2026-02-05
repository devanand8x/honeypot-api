import requests
import time
from datetime import datetime

# The health endpoint of our deployed API
URL = "https://honeypot-api-system.onrender.com/health"

def keep_alive():
    print("🚀 binary_geeks Keep-Alive Script is Running!")
    print(f"Target: {URL}")
    print("Sending pings every 60 seconds to prevent Render from sleeping...")
    print("-" * 50)

    while True:
        try:
            # Send a simple GET request to the health endpoint
            response = requests.get(URL, timeout=10)
            
            # Log the result with a timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if response.status_code == 200:
                print(f"[{timestamp}] ✅ Ping Successful! Status: 200 OK")
            else:
                print(f"[{timestamp}] ⚠️ Ping returned status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ❌ Network error: {e}")

        # Wait for 60 seconds before the next ping
        time.sleep(60)

if __name__ == "__main__":
    try:
        keep_alive()
    except KeyboardInterrupt:
        print("\n👋 Keep-Alive script stopped by user. API might sleep if idle.")
