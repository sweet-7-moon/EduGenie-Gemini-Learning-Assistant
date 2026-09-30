from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

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


class SummaryRequest(BaseModel):
    passage: str


class LearningPathRequest(BaseModel):
    topic: str
    level: str = "Beginner"
    goal: str = "Understand the topic"


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/qa")
def question_answer(question: str):
    try:
        return {
            "question": question,
            "answer": get_answer(question)
        }
    except Exception as exc:
        print(f"QA error: {exc}")
        raise HTTPException(
            status_code=502,
            detail=f"Could not generate an answer: {exc}"
        )


@app.get("/quiz")
def quiz(topic: str):
    try:
        return {
            "topic": topic,
            "quiz": generate_quiz(topic)
        }
    except Exception as exc:
        print(f"Quiz error: {exc}")
        raise HTTPException(
            status_code=502,
            detail=f"Could not generate the quiz: {exc}"
        )


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
            detail=f"Could not summarize the passage: {exc}"
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
            detail=f"Could not generate the learning path: {exc}"
        )