import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

try:
    models = client.models.list()
    for m in models:
        print(m.name)
except Exception as e:
    print("Error:", e)
