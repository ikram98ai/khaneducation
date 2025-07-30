# app/main.py
from fastapi import FastAPI, Depends # Remove: , HTTPException, status
# Remove: from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum
# Remove: from typing import List (if not used elsewhere)
from .ai import generate_content as ai
from . import schemas
from . import routers
# Remove: from . import models (SQLAlchemy models)
# Remove: from .database import get_db (SQLAlchemy session)

# --- PynamoDB Import ---
from .models import Subject, Lesson # Import models needed for AI context

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

@app.get("/languages", response_model=list[schemas.LanguageChoicesEnum]) # Use list type hint
def get_languages():
    return list(schemas.LanguageChoicesEnum)

# --- Updated AI Endpoint ---
# This endpoint needs to be adapted to fetch data using PynamoDB
@app.post("/ai/assist", response_model=dict)
def assist_user(request: schemas.AIContentRequest): # Remove db: Session = Depends(get_db)
    # --- Fetch context using PynamoDB ---
    try:
        subject = Subject.get(request.subject_id) # Fetch Subject by hash key (id)
    except Subject.DoesNotExist:
        subject = None

    lesson_content = ""
    if request.lesson_id:
        try:
            # Assuming Lesson uses subject_id as hash key and lesson id as range key
            # Adjust based on your actual PynamoDB Lesson model key structure
            lesson = Lesson.get(request.subject_id, request.lesson_id) # hash_key, range_key
            lesson_content = f"{lesson.title}" if lesson else ""
            lesson_content += f"\n{lesson.content}" if lesson else ""
        except Lesson.DoesNotExist:
            lesson = None
            lesson_content = ""

    context = f"Subject: {subject.name if subject else 'Unknown'}, Lesson: {lesson_content}"
    # --- End Fetch Context ---
    return {"ai_response": ai.ai_assistant(request.query_text, context)}

handler = Mangum(app)
