import json
import re

from modules.gemini_client import generate_text


def generate_quiz(topic: str) -> list:
    prompt = f"""
Create exactly 3 multiple-choice questions about: {topic}

Return only a valid JSON array.
Each question must contain:
- "question": a string
- "options": exactly 4 strings
- "answer": the exact text of the correct option

Use this format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }}
]

No Markdown and no explanations outside the JSON.
"""

    text = generate_text(prompt)

    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return valid quiz JSON.")

    quiz = json.loads(text[start:end + 1])

    if not isinstance(quiz, list) or len(quiz) != 3:
        raise ValueError("The quiz must contain exactly 3 questions.")

    for item in quiz:
        if not isinstance(item, dict):
            raise ValueError("Invalid quiz question format.")

        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")

        if (
            not isinstance(question, str)
            or not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(option, str) for option in options)
            or not isinstance(answer, str)
            or answer not in options
        ):
            raise ValueError("A quiz question has an invalid format.")

    return quiz