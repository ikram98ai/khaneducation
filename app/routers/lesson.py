from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from ..models import Lesson, User
from .. import schemas, database, services
from ..dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects/{subject_id}/lessons", tags=["lessons"])



@router.get("/", response_model=List[schemas.Lesson])
def read_lessons(
    subject_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    try:
        lessons = db.query(Lesson).filter(Lesson.subject_id == subject_id).offset(skip).limit(limit).all()
        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lessons found for this subject")
        return [schemas.Lesson.from_orm(lesson) for lesson in lessons]
    except SQLAlchemyError as e:
        logger.error(f"Error fetching lessons for subject {subject_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{lesson_id}", response_model=List[schemas.Lesson])
def read_lesson(
    subject_id: int,
    lesson_id: int,
    db: Session = Depends(database.get_db),
):
    try:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.subject_id == subject_id).first()
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lesson found for this subject")
        return schemas.Lesson.from_orm(lesson)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching lesson {lesson_id} for subject {subject_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

