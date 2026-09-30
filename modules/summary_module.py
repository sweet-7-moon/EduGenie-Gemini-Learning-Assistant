from modules.gemini_client import generate_text


def summarize_passage(passage: str) -> str:
    prompt = f"""
Summarize this passage for a student using simple language.

Include:
1. A short overview
2. The main points
3. Important terms, if relevant
4. One concluding sentence

Do not add facts that are not in the passage.
Keep the summary concise.

PASSAGE:
{passage}
"""
    return generate_text(prompt)