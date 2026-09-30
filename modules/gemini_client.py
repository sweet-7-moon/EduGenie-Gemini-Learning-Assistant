import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your project's .env file."
    )

MODEL = "gemini-3.5-flash-lite"

client = genai.Client(api_key=API_KEY)

_cache = {}


def generate_text(prompt: str) -> str:
    if prompt in _cache:
        return _cache[prompt]

    start_time = time.perf_counter()

    try:
        response = client.interactions.create(
            model=MODEL,
            input=prompt
        )

        answer = response.output_text

        if not answer or not answer.strip():
            raise RuntimeError("Gemini returned an empty response.")

        answer = answer.strip()
        _cache[prompt] = answer
        return answer

    except Exception as exc:
        if "429" in str(exc):
            raise RuntimeError(
                "Free daily limit reached for this model. "
                "Wait for the reset or change MODEL."
            ) from exc
        raise

    finally:
        elapsed = time.perf_counter() - start_time
        print(f"Gemini API request time: {elapsed:.2f} seconds")