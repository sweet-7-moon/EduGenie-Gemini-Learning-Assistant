
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from modules.qna import get_answer
from modules.quiz_module import generate_quiz
from modules.summary_module import summarize_passage
from modules.learning_path import generate_learning_path


app = FastAPI(title="EduGenie - AI Learning Assistant")

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Temporary server-side storage for generated quizzes.
# Correct answers and explanations are not sent before submission.
quiz_store = {}


class SummaryRequest(BaseModel):
    passage: str


class LearningPathRequest(BaseModel):
    topic: str
    level: str = "Beginner"
    goal: str = "Understand the topic"


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: list[int] = Field(min_length=1, max_length=50)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/qa")
def question_answer(question: str):
    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        return {
            "question": question,
            "answer": get_answer(question)
        }
    except Exception as exc:
        print(f"QA error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not generate an answer."
        )


@app.get("/quiz")
def quiz(topic: str):
    if not topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a quiz topic."
        )

    try:
        generated_quiz = generate_quiz(topic)

        if not isinstance(generated_quiz, list) or not generated_quiz:
            raise ValueError("The quiz generator returned no questions.")

        if len(generated_quiz) > 50:
            raise ValueError("The quiz contains too many questions.")

        public_questions = []
        answer_key = []

        for item in generated_quiz:
            if not isinstance(item, dict):
                raise ValueError("Invalid quiz question format.")

            question = item.get("question")
            options = item.get("options")
            answer = item.get("answer")

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

            correct_index = options.index(answer)

            # Use the generated explanation when available.
            explanation = item.get("explanation", "")

            # Fallback if no explanation was generated.
            if not isinstance(explanation, str) or not explanation.strip():
                explanation = (
                    f"The correct answer is '{answer}'. "
                    f"It is the correct option for this question "
                    f"about {topic}."
                )

            # Keep answers and explanations on the server.
            answer_key.append({
                "correct_index": correct_index,
                "correct_answer": answer,
                "explanation": explanation
            })

            # Only questions and options are sent to the browser.
            public_questions.append({
                "question": question,
                "options": options
            })

        quiz_id = str(uuid4())

        quiz_store[quiz_id] = {
            "topic": topic,
            "questions": public_questions,
            "answer_key": answer_key
        }

        return {
            "topic": topic,
            "quiz_id": quiz_id,
            "quiz": public_questions
        }

    except Exception as exc:
        print(f"Quiz generation error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not generate the quiz. Please try again."
        )


@app.post("/quiz/submit")
def submit_quiz(request: QuizSubmitRequest):
    stored_quiz = quiz_store.get(request.quiz_id)

    if stored_quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz not found. Please generate a new quiz."
        )

    questions = stored_quiz["questions"]
    answer_key = stored_quiz["answer_key"]

    if len(request.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail="Please answer every question before submitting."
        )

    results = []
    score = 0

    for index, selected_index in enumerate(request.answers):
        options = questions[index]["options"]

        if not 0 <= selected_index < len(options):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid option for question {index + 1}."
            )

        correct_index = answer_key[index]["correct_index"]
        is_correct = selected_index == correct_index

        if is_correct:
            score += 1

        result_item = {
            "correct": is_correct
        }

        # Reveal the correct answer and explanation only
        # when the submitted answer is incorrect.
        if not is_correct:
            result_item["correct_answer"] = (
                answer_key[index]["correct_answer"]
            )

            explanation = answer_key[index]["explanation"]

            if isinstance(explanation, str) and explanation.strip():
                result_item["explanation"] = explanation

        results.append(result_item)

    return {
        "topic": stored_quiz["topic"],
        "score": score,
        "total": len(questions),
        "results": results
    }


@app.post("/summarize")
def summarize(request: SummaryRequest):
    if not request.passage.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a passage to summarize."
        )

    try:
        return {
            "summary": summarize_passage(request.passage)
        }
    except Exception as exc:
        print(f"Summary error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not summarize the passage."
        )


@app.post("/learn/recommendations")
def learning_recommendations(request: LearningPathRequest):
    if not request.topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a learning topic."
        )

    try:
        return {
            "learning_path": generate_learning_path(
                topic=request.topic,
                level=request.level,
                goal=request.goal
            )
        }
    except Exception as exc:
        print(f"Learning path error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not generate the learning path."
        )