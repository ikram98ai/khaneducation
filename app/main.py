from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum

from .routers import (
    user,
    auth,
    subject,
    lesson,
    task,
    quiz,
    student,
    base,
    dashboard,
    admin,
)


app = FastAPI(version="1.0.0")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(subject.router)
app.include_router(lesson.router)
app.include_router(task.router)
app.include_router(quiz.router)
app.include_router(base.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return RedirectResponse("/docs")


handler = Mangum(app)
