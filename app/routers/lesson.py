from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging
from .. import schemas, crud, database, models, services
from ..dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects/{subject_id}/lessons", tags=["lessons"])


@router.post("/", response_model=schemas.Lesson)
def create_lesson(
    subject_id: int,
    lesson: schemas.LessonCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return services.create_lesson_with_content(db, subject_id, current_user.id, lesson.title)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Error creating lesson for subject {subject_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/", response_model=List[schemas.Lesson])
def read_lessons(
    subject_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    try:
        lessons = db.query(models.Lesson).filter(models.Lesson.subject_id == subject_id).offset(skip).limit(limit).all()
        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lessons found for this subject")
        return lessons
    except SQLAlchemyError as e:
        logger.error(f"Error fetching lessons for subject {subject_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.put("/{lesson_id}/verify", response_model=schemas.Lesson)
def verify_lesson(lesson_id: int, db: Session = Depends(database.get_db)):
    try:
        lesson = crud.crud_lesson.get(db, lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        lesson.status = models.LessonStatus.VERIFIED
        lesson.verified_at = datetime.utcnow()
        db.commit()
        return lesson
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error verifying lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
