from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum

from . import routers

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
app.include_router(routers.base.router)
app.include_router(routers.dashboard.router)
app.include_router(routers.admin.router)


@app.get("/")
def root():
    return RedirectResponse("/docs")


handler = Mangum(app)
