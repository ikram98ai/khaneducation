# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum
from .ai import generate_content as ai
from . import schemas
from . import routers

# --- PynamoDB Import ---
from .models import Subject, Lesson  # Import models needed for AI context

app = FastAPI(version="1.0.0")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.user_profile.router)
app.include_router(routers.auth.router)
app.include_router(routers.subject.router)
app.include_router(routers.lesson.router)
app.include_router(routers.quiz.router)
app.include_router(routers.dashboard.router)
app.include_router(routers.admin.router)


@app.get("/")
def root():
    return RedirectResponse("/docs")


@app.get("/languages", response_model=list[schemas.LanguageChoicesEnum])  # Use list type hint
def get_languages():
    return list(schemas.LanguageChoicesEnum)


@app.post("/ai/assist", response_model=dict)
async def assist_user(request: schemas.AIContentRequest):
    try:
        subject = Subject.get(request.subject_id)  # Fetch Subject by hash key (id)
    except Subject.DoesNotExist:
        subject = None

    lesson_content = ""
    if request.lesson_id:
        try:
            lesson = Lesson.get(request.lesson_id)  # hash_key, range_key
            lesson_content = f"{lesson.title}" if lesson else ""
            lesson_content += f"\n{lesson.content}" if lesson else ""
        except Lesson.DoesNotExist:
            lesson = None
            lesson_content = ""

    context = f"Subject: {subject.name if subject else 'Unknown'}, Lesson: {lesson_content}"
    # --- End Fetch Context ---
    response = await  ai.ai_assistant(request.user_messages, context)
    return {"ai_response":response}


handler = Mangum(app)
