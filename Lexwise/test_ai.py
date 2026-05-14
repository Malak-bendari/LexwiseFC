import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")

try:
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="Hello, are you working?")],
        ),
    ]

    config = types.GenerateContentConfig(
        system_instruction="You are a helpful assistant.",
        temperature=0.7,
        max_output_tokens=50,
    )

    response = client.models.generate_content(
        model="gemma-4-26b-a4b-it",
        contents=contents,
        config=config,
    )
    print("Success:", response.text)
except Exception as e:
    import traceback
    print("Error:", e)
    traceback.print_exc()
