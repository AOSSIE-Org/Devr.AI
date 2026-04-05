import requests
import json
import os
from dotenv import load_dotenv

# Load .env from compiled path or current directory
load_dotenv()

SECRET_TOKEN = os.getenv('SECRET_TOKEN')

url = "http://127.0.0.1:5000/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": SECRET_TOKEN
}
payload = {
    "msg": "What is the purpose of Extractor.py?",
    "repo": "DhruvK278/AutoPDFCleaner",
    "model": "openrouter/google/gemini-2.0-flash-001"
}

try:
    print(f"Sending request to {url} with payload: {payload}")
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response Text:")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
