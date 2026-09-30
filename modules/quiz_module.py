
import json
import re

from modules.gemini_client import generate_text


def generate_quiz(topic: str) -> list:
    prompt = f"""
Create exactly 3 multiple-choice questions about: {topic}

The questions should be suitable for beginner-level learners.

Return only a valid JSON array.
Each question must contain:
- "question": a clear question as a string
- "options": exactly 4 strings
- "answer": the exact text of the correct option
- "explanation": a short explanation in simple English

Explanation requirements:
- Use 2-3 short sentences.
- Explain why the correct answer is right.
- Use simple words that beginners can understand.
- Explain technical terms briefly when needed.
- Avoid long paragraphs and unnecessary details.
- Do not merely repeat the correct answer.

Use this format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A",
    "explanation": "Explain simply why Option A is correct."
  }}
]

Ensure each answer exactly matches one of the four options.
Ensure every explanation is relevant to the question and factually correct.
Return valid JSON only, without Markdown or extra text.
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
        explanation = item.get("explanation")

        if (
            not isinstance(question, str)
            or not question.strip()
            or not isinstance(options, list)
            or len(options) != 4
            or not all(
                isinstance(option, str) and option.strip()
                for option in options
            )
            or not isinstance(answer, str)
            or answer not in options
        ):
            raise ValueError("A quiz question has an invalid format.")

        # Use a fallback only if Gemini omits the explanation.
        if not isinstance(explanation, str) or not explanation.strip():
            item["explanation"] = (
                "A detailed explanation was not generated. "
                "Please try generating the quiz again."
            )

    return quiz