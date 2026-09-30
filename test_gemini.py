import os
from dotenv import load_dotenv
from google import genai

MODEL = "gemini-3.5-flash"

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model=MODEL,
    contents="Which is the largest ocean? Answer in one line."
)
print(response.text)