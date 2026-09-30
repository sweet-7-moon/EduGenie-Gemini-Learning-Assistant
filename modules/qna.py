from modules.gemini_client import generate_text


def get_answer(question: str) -> str:
    prompt = f"""
Answer the student's question in simple, clear language.
Keep the answer concise and include an example when useful.

Question: {question}
"""
    return generate_text(prompt)