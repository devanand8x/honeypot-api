import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing API Key: {api_key[:10]}...")

genai.configure(api_key=api_key)

print("\n--- Listing available models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\n--- Testing Gemini 1.5 Flash ---")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hi")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Failed to use gemini-1.5-flash: {e}")

print("\n--- Testing Gemini Pro (Legacy/Stable) ---")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hi")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Failed to use gemini-pro: {e}")
