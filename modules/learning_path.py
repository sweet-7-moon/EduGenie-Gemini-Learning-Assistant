from modules.gemini_client import generate_text


def generate_learning_path(
    topic: str,
    level: str = "Beginner",
    goal: str = "Understand the topic"
) -> str:
    prompt = f"""
Create a practical, concise learning plan for a student.

Topic: {topic}
Current level: {level}
Goal: {goal}

Include:
1. Prerequisites
2. Five learning steps in order
3. A short activity for each step
4. One small final project or assessment
5. A way to review progress

Use simple language and clear headings.
Make realistic recommendations.
Do not assume abilities not mentioned by the student.
"""
    return generate_text(prompt)