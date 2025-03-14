


# # from sqlalchemy.pool import NullPool
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env
# load_dotenv()

# # ChatGroq API keys
# CHATGROQ_API_URL_TRANSCRIBE = "https://api.groq.com/openai/v1/audio/transcriptions"
# CHATGROQ_API_URL_CHAT = "https://api.groq.com/openai/v1/chat/completions"
# API_KEY = os.getenv("GROQ_API_KEY")

# import requests

# def query_sponsorship_client(info):
#     prompt = f"Extract key details about sponsorship and client interactions from the following:\n\n{info}\n\nRespond in JSON with 'sponsorship_details' and 'client_interaction_summary'."

#     headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
#     payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0}

#     try:
#         response = requests.post(CHATGROQ_API_URL_CHAT, json=payload, headers=headers)
#         return response.json().get("choices", [{}])[0].get("message", {}).get("content", {})
#     except Exception as e:
#         return {"error": str(e)}
