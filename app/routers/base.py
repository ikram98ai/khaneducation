from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from typing import List
from ..ai import generate_content as ai

router = APIRouter()


@router.get("/languages", response_model=List[schemas.LanguageChoices])
def get_languages():
    return list(schemas.LanguageChoices)


@router.post("/assist", response_model=dict)
def assist_user(request: schemas.AIContentRequest, db: Session = Depends(get_db)):
    return {"response": ai.ai_assistant(request.message, request.context)}
