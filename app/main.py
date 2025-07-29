from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .ai import generate_content as ai
from . import schemas
from . import routers
from . import models

app = FastAPI(version="1.0.0")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.user.router)
app.include_router(routers.auth.router)
app.include_router(routers.subject.router)
app.include_router(routers.lesson.router)
app.include_router(routers.quiz.router)
app.include_router(routers.dashboard.router)
app.include_router(routers.admin.router)


@app.get("/")
def root():
    return RedirectResponse("/docs")


@app.get("/languages", response_model=List[schemas.LanguageChoices])
def get_languages():
    return list(schemas.LanguageChoices)


@app.post("/ai/assist", response_model=dict)
def assist_user(request: schemas.AIContentRequest, db: Session = Depends(get_db)):
    # load subject name and lesson name from the database if needed
    # For now, we assume that the subject_id and lesson_id are sufficient for context
    # If you need to fetch additional context, you can do so here
    # For example:
    subject = db.query(models.Subject).filter(models.Subject.id == request.subject_id).first()
    lesson_content = ""
    if request.lesson_id:
        lesson = db.query(models.Lesson).filter(models.Lesson.id == request.lesson_id).first()
        lesson_content = f"{lesson.title}" if lesson else ""
        lesson_content += f"\n\{lesson.content}" if lesson else ""

    context = f"Subject: {subject.name}, Lesson: {lesson_content}"

    return {"ai_response": ai.ai_assistant(request.query_text, context)}


handler = Mangum(app)
